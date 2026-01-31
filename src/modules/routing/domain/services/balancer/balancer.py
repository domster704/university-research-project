from src.modules.routing.domain.entities.node_metrics import NodeMetrics
from src.modules.routing.domain.strategies.ranking_strategy import RankingStrategy


class Balancer:
    def __init__(self, strategy: RankingStrategy):
        self.strategy = strategy

    def choose(self, metrics: list[NodeMetrics]) -> str:
        if not metrics:
            raise ValueError("No available nodes")

        idx = self.strategy.choose(metrics)
        return metrics[idx].node_id
