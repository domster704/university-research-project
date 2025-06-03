"""Сбор свежих метрик с Docker-нод через docker-SDK."""

from __future__ import annotations

import asyncio
import time
from pprint import pprint
from types import SimpleNamespace
from typing import Dict

import aiodocker
from aiodocker.containers import DockerContainer

import config
from models import NodeMetrics

_ready = asyncio.Event()
_prev: Dict[str, NodeMetrics] = {}  # node_id -> последний снимок
# snapshot: Dict[str, NodeMetrics] = {}  # node_id -> актуальный снимок

COLLECT_METRICS_ACTIONS_INTERVAL = 0.25


async def get_container_stats(container: DockerContainer):
    return (await container.stats(stream=False))[0]


class CollectorManager:
    MAX_AGE_SECONDS = 1.0  # cколько секунд метрики считаются свежими

    def __init__(self):
        self.snapshot: dict[str, NodeMetrics] = {}
        self._last_update = 0.0
        self._lock = asyncio.Lock()

    @staticmethod
    async def _get_port(container: DockerContainer):
        """
        "Networks": {
            ...
            "Ports": {
              "8002/tcp": [
                {
                  "HostIp": "0.0.0.0",
                  "HostPort": "8002"
                }
              ]
            },
            ...
          }
        """

        container_namespace = SimpleNamespace(**await container.show())
        port: int = int(
            next(iter(
                container_namespace.NetworkSettings['Ports'].values()
            ))[0]["HostPort"]
        )
        return port

    async def _collect_once(self):
        docker = aiodocker.Docker()

        containers: list[DockerContainer] = await docker.containers.list()
        tasks = [get_container_stats(c) for c in containers]
        stats_list = await asyncio.gather(*tasks, return_exceptions=True)
        print("Обновление метрик...")

        async with self._lock:
            for container, stats in zip(containers, stats_list):
                if isinstance(stats, Exception):
                    continue

                container_namespace = SimpleNamespace(**await container.show())

                # Node ID
                node_id = container_namespace.Name.replace('/', '')

                # CPU %
                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                            stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                               stats["precpu_stats"]["system_cpu_usage"]
                cpu_util = cpu_delta / (system_delta + 1e-12) * stats['cpu_stats']['online_cpus'] * 100

                # MEM %
                mem_util = stats["memory_stats"]["usage"] / stats["memory_stats"]["limit"] * 100

                # NET bytes
                net_sum = stats.get("networks", {})
                net_in = sum(n["rx_bytes"] for n in net_sum.values()) if net_sum else 0
                net_out = sum(n["tx_bytes"] for n in net_sum.values()) if net_sum else 0

                node_metrics = NodeMetrics(
                    timestamp=NodeMetrics.now_iso(),
                    node_id=node_id,
                    cpu_util=float(cpu_util),
                    mem_util=float(mem_util),
                    net_in_bytes=int(net_in),
                    net_out_bytes=int(net_out),
                )

                self.snapshot[node_id] = node_metrics
                config.update_node_endpoints({
                    node_id: await self._get_port(container)
                })

            self._last_update = time.time()
            _prev.update(self.snapshot)

        await docker.close()

    async def run_forever(self):
        while True:
            try:
                await self._collect_once()
            except Exception as e:
                print("metrics collection failed: ", e.with_traceback())
            await asyncio.sleep(config.COLLECT_PERIOD)

    async def ensure_fresh(self):
        """Обновить, только если данные старее, чем MAX_AGE."""
        if time.time() - self._last_update < self.MAX_AGE_SECONDS:
            return

        print("Обновление метрик из-за старых данных...")
        async with self._lock:  # защита от параллельных запросов
            if time.time() - self._last_update < self.MAX_AGE_SECONDS:
                return  # другой корутин уже успел
            await self._collect_once()

    def get_metrics(self) -> dict[str, NodeMetrics]:
        # читаем без await, но под блокировкой – чтобы не поймать частичный апдейт
        return list(self.snapshot.values())


async def wait_ready(timeout: float = 10.0):
    """Блокируется, пока не появятся первые метрики."""
    try:
        await asyncio.wait_for(_ready.wait(), timeout)
    except asyncio.TimeoutError:
        raise TimeoutError("Не удалось собрать метрики за время ожидания")


def get_prev(node_id: str) -> Dict[str, NodeMetrics]:
    """Возвращает копию предыдущего среза."""
    return _prev[node_id]
