import numpy as np

from src.modules.mcdm.algorithms.topsis import topsis
from src.modules.routing.domain.policies.ranking_strategy import RankingStrategy


class TopsisStrategy(RankingStrategy):
    def choose(self, scores: np.ndarray, weights: np.ndarray) -> int:
        return topsis(scores, weights)
