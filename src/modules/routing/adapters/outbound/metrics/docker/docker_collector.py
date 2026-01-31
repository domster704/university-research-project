from __future__ import annotations

import asyncio
from types import SimpleNamespace

import aiodocker
from aiodocker.containers import DockerContainer

from src.modules.routing.application.ports.outbound.metrics.metrics_repository import MetricsRepository
from src.modules.routing.domain.entities.node.node_metrics import NodeMetrics


async def _get_container_stats(container: DockerContainer) -> dict:
    # aiodocker возвращает список, берём [0]
    return (await container.stats(stream=False))[0]


async def _get_host_port(container: DockerContainer) -> int:
    """
    Достаём HostPort из NetworkSettings.Ports.
    """
    ns = SimpleNamespace(**await container.show())
    ports = ns.NetworkSettings["Ports"]
    first = next(iter(ports.values()))
    return int(first[0]["HostPort"])


class DockerMetricsCollector:
    """
    Коллектор:
      - ходит в Docker
      - собирает raw stats
      - пишет нормализованные метрики в репозиторий
    Не хранит snapshot/prev у себя.
    """

    def __init__(self, repo: MetricsRepository, registry_updater):
        self.repo = repo
        self.registry_updater = registry_updater  # callback/adapter для обновления endpoints

    async def collect_once(self) -> None:
        docker = aiodocker.Docker()
        try:
            containers: list[DockerContainer] = await docker.containers.list()
            stats_list = await asyncio.gather(
                *[_get_container_stats(c) for c in containers],
                return_exceptions=True,
            )

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
                cpu_util = cpu_delta / (system_delta + 1e-12) * stats['cpu_stats']['online_cpus']

                # MEM %
                mem_util = stats["memory_stats"]["usage"] / stats["memory_stats"]["limit"]

                # NET bytes
                net_sum = stats.get("networks", {})
                net_in = sum(n["rx_bytes"] for n in net_sum.values()) if net_sum else 0
                net_out = sum(n["tx_bytes"] for n in net_sum.values()) if net_sum else 0

                metrics = NodeMetrics(
                    node_id=node_id,
                    timestamp=NodeMetrics.now(),
                    cpu_util=float(cpu_util),
                    mem_util=float(mem_util),
                    net_in_bytes=int(net_in),
                    net_out_bytes=int(net_out),
                )
                self.repo.upsert(metrics)

                # обновим endpoint (host/port) через отдельный адаптер
                port = await _get_host_port(container)
                self.registry_updater.update(node_id=node_id, host="127.0.0.1", port=port)

        finally:
            await docker.close()
