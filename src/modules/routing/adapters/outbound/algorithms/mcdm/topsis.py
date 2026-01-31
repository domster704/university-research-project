import numpy as np

from src.modules.mcdm.algorithms.topsis import topsis
from src.modules.routing.domain.entities.node_metrics import NodeMetrics
from src.modules.routing.domain.strategies.ranking_strategy import RankingStrategy


class TopsisStrategy(RankingStrategy):
    def choose(self, metrics: list[NodeMetrics]) -> str:
        x = np.array([
            [m.cpu_util, m.mem_util, m.net_util]
            for m in metrics
        ])
        w = np.array([0.4, 0.3, 0.3])

        idx = topsis(x, w)
        return metrics[idx].node_id
