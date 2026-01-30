import numpy as np

from src.domain.entities.node_metrics import NodeMetrics


class Balancer:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def choose(self, metrics: list[NodeMetrics]) -> str:
        if not metrics:
            raise ValueError("No available nodes")

        X = np.array([
            [m.cpu_util, m.mem_util, m.net_util]
            for m in metrics
        ])

        idx = self.algorithm(X)
        return metrics[idx].node_id

    def rank(self, metrics: list[NodeMetrics]) -> list[NodeMetrics]:
        X = np.array([
            [m.cpu_util, m.mem_util, m.net_util]
            for m in metrics
        ])
        order = self.algorithm.rank(X)
        return [metrics[i] for i in order]
