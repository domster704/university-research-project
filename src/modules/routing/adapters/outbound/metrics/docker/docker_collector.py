from __future__ import annotations

import asyncio
from types import SimpleNamespace

import aiodocker
from aiodocker.containers import DockerContainer

from src.modules.routing.application.ports.outbound.metrics.collector import CollectorManager
from src.modules.routing.application.ports.outbound.metrics.metrics_repository import MetricsRepository
from src.modules.routing.application.ports.outbound.node.node_registry import NodeRegistry
from src.modules.routing.domain.entities.node.node_metrics import NodeMetrics
from src.modules.routing.domain.strategies.metric_extractor import MetricExtractor


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


class DockerMetricsCollector(CollectorManager):
    """
    Коллектор:
      - ходит в Docker
      - собирает raw stats
      - пишет нормализованные метрики в репозиторий
    Не хранит snapshot/prev у себя.
    """

    def __init__(
            self,
            repo: MetricsRepository,
            registry_updater: NodeRegistry,
            extractors: list[MetricExtractor],
    ):
        self.repo = repo
        self.registry_updater = registry_updater
        self.extractors = extractors

    async def collect(self) -> None:
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
                node_id = container_namespace.Name.replace('/', '')

                values: dict[str, float] = {}
                for extractor in self.extractors:
                    values.update(extractor.extract(stats))

                metrics = NodeMetrics(
                    node_id=node_id,
                    timestamp=NodeMetrics.now(),
                    **values,
                )
                self.repo.upsert(metrics)

                # обновим endpoint (host/port) через отдельный адаптер
                port = await _get_host_port(container)
                self.registry_updater.update(
                    node_id=node_id,
                    host="127.0.0.1",
                    port=port
                )

        finally:
            await docker.close()
