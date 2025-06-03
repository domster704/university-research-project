# collector.py
"""Сбор свежих метрик с Docker-нод через docker-SDK."""

from __future__ import annotations

import asyncio
from pprint import pprint
from typing import Dict, List

import docker

import config
from models import NodeMetrics

_ready = asyncio.Event()
_client = docker.from_env()
_prev: Dict[str, NodeMetrics] = {}  # node_id -> последний снимок
snapshot: Dict[str, NodeMetrics] = {}  # node_id -> актуальный снимок


async def collect_loop():
    """Асинхронный цикл обновления `_snapshot`."""
    while True:
        # TODO: добавить map для node_id (stats['id']): server_ip (из container.attrs)
        await asyncio.sleep(config.COLLECT_PERIOD)
        for container in _client.containers.list():
            stats = container.stats(stream=False)

            node_id = container.attrs["Name"] if container.attrs.get("Name") else "local"
            node_id = node_id.replace('/', '')

            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                        stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                           stats["precpu_stats"]["system_cpu_usage"]
            cpu_util = cpu_delta / (system_delta + 1e-12) * stats['cpu_stats']['online_cpus'] * 100

            mem_util = stats["memory_stats"]["usage"] / stats["memory_stats"]["limit"] * 100

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
            snapshot[node_id] = node_metrics
            pprint(snapshot)

        _prev.update(snapshot)


async def wait_ready(timeout: float = 5.0):
    """Блокируется, пока не появятся первые метрики."""
    try:
        await asyncio.wait_for(_ready.wait(), timeout)
    except asyncio.TimeoutError:
        # Если что-то пошло не так — подразумеваем хотя бы один dummy-узел
        if not snapshot:
            snapshot["dummy"] = NodeMetrics(
                timestamp=NodeMetrics.now_iso(),
                node_id="dummy",
                cpu_util=0.0,
                mem_util=0.0,
                net_in_bytes=0,
                net_out_bytes=0,
            )


def get_metrics() -> List[NodeMetrics]:
    """Возвращает копию последнего среза."""
    return list(snapshot.values())


def get_prev(node_id: str) -> Dict[str, NodeMetrics]:
    """Возвращает копию предыдущего среза."""
    return _prev[node_id]
