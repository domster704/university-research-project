from src.modules.mcdm.algorithms.lc import lc
from src.modules.routing.domain.policies.ranking_strategy import RankingStrategy
from src.modules.types.numpy import Matrix, Vector


class LinearScalarizationStrategy(RankingStrategy):
    def choose(self, scores: Matrix, weights: Vector) -> int:
        return lc(scores, weights)
