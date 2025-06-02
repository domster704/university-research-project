# app.py
"""FastAPI-прокси: перенаправляет запросы на выбранную Docker-ноду."""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict

import httpx
import uvicorn
from fastapi import FastAPI, Request, Response

import balancer
import collector
import config

# скользящее окно задержек
_latency: Dict[str, list[float]] = {}


def update_latency(node_id: str, dt_ms: float, window: int = config.LAT_WINDOW):
    """Обновляет среднюю задержку заданного узла."""
    buf = _latency.setdefault(node_id, [])
    buf.append(dt_ms)
    if len(buf) > window:
        buf.pop(0)
    # пишем в глобальный снимок
    if node_id in collector.snapshot:
        collector.snapshot[node_id].latency_ms = sum(buf) / len(buf)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(collector.collect_loop())
    yield
    pass


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def proxy(request: Request, call_next):
    """
    Middleware, заменяющая обычную обработку на проксирование.
    """
    metrics = collector.get_metrics()
    node = balancer.choose_node(metrics, alg_name=request.headers.get("X-Balancer", config.DEFAULT_ALGORITHM))

    target_url = f"http://{node}:{request.url.port}{request.url.path}"
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        resp = await client.request(
            request.method,
            target_url,
            params=request.query_params,
            headers=request.headers.raw,
            content=await request.body(),
            timeout=None,
        )
        dt = (time.perf_counter() - start) * 1_000
        update_latency(node, dt)

    proxy_resp = Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=resp.headers,
    )
    return proxy_resp


if __name__ == "__main__":
    uvicorn.run("app:app", port=8000, reload=True)
