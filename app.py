"""FastAPI-прокси: перенаправляет запросы на выбранную Docker-ноду."""
from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from pprint import pprint
from types import SimpleNamespace
from typing import Dict

import aiodocker
import aiohttp
import uvicorn
from aiodocker.containers import DockerContainer
from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse

import balancer
import collector
import config

# скользящее окно задержек
_latency: Dict[str, list[float]] = {}
collector_manager = collector.CollectorManager()
clientSession: aiohttp.ClientSession | None = None


def update_latency(node_id: str, dt_ms: float, window: int = config.LAT_WINDOW):
    """Обновляет среднюю задержку заданного узла."""
    buf = _latency.setdefault(node_id, [])
    buf.append(dt_ms)
    if len(buf) > window:
        buf.pop(0)
    # пишем в глобальный снимок
    if node_id in collector_manager.snapshot:
        collector_manager.snapshot[node_id].latency_ms = sum(buf) / len(buf)


async def main():
    docker = aiodocker.Docker()

    containers: list[DockerContainer] = await docker.containers.list()
    pprint(containers)
    for container in containers:
        stats = await container.stats(stream=False)
        namespace = SimpleNamespace(**await container.show())

        pprint(namespace)
        break
    await docker.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    clientSession = aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=100, ttl_dns_cache=300),
        timeout=aiohttp.ClientTimeout(total=30),
    )

    collector_task = asyncio.create_task(collector_manager.run_forever())

    yield

    await clientSession.close()
    collector_task.cancel()


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def proxy(request: Request, call_next):
    """
    Middleware, заменяющая обычную обработку на проксирование.
    """
    # await collector_manager.ensure_fresh()
    metrics = collector_manager.get_metrics()

    start = time.time()
    node = balancer.choose_node(metrics, alg_name=request.headers.get("X-Balancer", config.DEFAULT_ALGORITHM))
    elapsed = time.time() - start
    print(f"Время выполнения: {elapsed:.12f} секунд")

    try:
        host, port = config.NODE_ENDPOINTS[node]
    except KeyError:
        return JSONResponse(
            {"detail": f"Неизвестный node_id '{node}' (нет в NODE_ENDPOINTS)"},
            status_code=502
        )

    target_url = f"http://{host}:{port}{request.url.path}"

    headers = {k: v for k, v in request.headers.items()}
    start = time.perf_counter()

    async with clientSession.request(
            request.method,
            target_url,
            params=request.query_params,
            headers=headers,
            data=await request.body(),
    ) as resp:
        body = await resp.read()

    dt = (time.perf_counter() - start) * 1_000
    update_latency(node, dt)

    return Response(content=body,
                    status_code=resp.status,
                    headers=resp.headers)


if __name__ == "__main__":
    uvicorn.run(
        app,
        port=8000,
        loop="asyncio",
        factory=False,
    )
