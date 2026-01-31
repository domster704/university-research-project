import numpy as np

from src.modules.routing.domain.strategies.ranking_strategy import RankingStrategy


class Balancer:
    def __init__(self, strategy: RankingStrategy):
        self.strategy = strategy

    def choose(self, scores: np.ndarray, weights: np.ndarray) -> int:
        idx = self.strategy.choose(scores, weights)
        return idx
