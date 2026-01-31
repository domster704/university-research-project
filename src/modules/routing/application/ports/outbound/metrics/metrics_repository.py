from typing import Protocol

from src.modules.routing.domain.entities.node.node_metrics import NodeMetrics


class MetricsRepository(Protocol):
    def upsert(self, metrics: NodeMetrics) -> None:
        ...

    def get_latest(self, node_id: str) -> NodeMetrics | None:
        ...

    def list_latest(self) -> list[NodeMetrics]:
        ...

    def get_prev(self, node_id: str) -> NodeMetrics | None:
        ...

    def add_latency(self, node_id: str, latency_ms: float) -> None:
        ...

    def get_latency_window(self, node_id: str) -> list[float]:
        ...
