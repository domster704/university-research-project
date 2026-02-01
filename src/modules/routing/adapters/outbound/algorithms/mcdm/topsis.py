from src.modules.mcdm.algorithms.topsis import topsis
from src.modules.routing.domain.policies.ranking_strategy import RankingStrategy
from src.modules.types.numpy import Matrix, Vector


class TopsisStrategy(RankingStrategy):
    def choose(self, scores: Matrix, weights: Vector) -> int:
        return topsis(scores, weights)
