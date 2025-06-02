# collector.py
"""Сбор свежих метрик с Docker-нод через docker-SDK."""

from __future__ import annotations

import asyncio
from pprint import pprint
from typing import Dict, List

import docker

import config
from models import NodeMetrics

_client = docker.from_env()
_prev: Dict[str, NodeMetrics] = {}  # node_id -> последний снимок
snapshot: Dict[str, NodeMetrics] = {}  # node_id -> актуальный снимок


async def collect_loop():
    """Асинхронный цикл обновления `_snapshot`."""
    while True:
        await asyncio.sleep(config.COLLECT_PERIOD)
        for container in _client.containers.list():
            stats = container.stats(stream=False)
            node_id = container.attrs["Node"]["Name"] if container.attrs.get("Node") else "local"
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                        stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                           stats["precpu_stats"]["system_cpu_usage"]
            cpu_util = cpu_delta / (system_delta + 1e-12)

            mem_util = stats["memory_stats"]["usage"] / \
                       max(stats["memory_stats"]["limit"], 1)

            net_sum = stats.get("networks", {})
            net_in = sum(n["rx_bytes"] for n in net_sum.values()) if net_sum else 0
            net_out = sum(n["tx_bytes"] for n in net_sum.values()) if net_sum else 0

            nm = NodeMetrics(
                timestamp=NodeMetrics.now_iso(),
                node_id=node_id,
                cpu_util=float(cpu_util),
                mem_util=float(mem_util),
                net_in_bytes=int(net_in),
                net_out_bytes=int(net_out),
            )
            snapshot[node_id] = nm
            pprint(snapshot)
        # сдвигаем prev
        _prev.update(snapshot)


def get_metrics() -> List[NodeMetrics]:
    """Возвращает копию последнего среза."""
    return list(snapshot.values())
