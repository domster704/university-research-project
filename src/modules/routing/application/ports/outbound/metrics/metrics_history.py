from typing import Protocol

from src.modules.routing.domain.entities.node.node_metrics import NodeMetrics


class MetricsHistory(Protocol):
    def get_prev(self, node_id: str) -> NodeMetrics | None:
        ...
