from typing import Protocol

from src.domain.entities.node_metrics import NodeMetrics


class MetricsProvider(Protocol):
    async def get_current(self) -> list[NodeMetrics]:
        ...
