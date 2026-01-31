from typing import Protocol

from src.modules.routing.domain.entities.node_metrics import NodeMetrics


class RankingStrategy(Protocol):
    def choose(self, metrics: list[NodeMetrics]) -> str:
        ...
