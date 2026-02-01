from src.modules.mcdm.algorithms.airm import airm
from src.modules.routing.domain.policies.ranking_strategy import RankingStrategy
from src.modules.types.numpy import Matrix, Vector


class AIRMStrategy(RankingStrategy):
    def choose(self, scores: Matrix, weights: Vector) -> int:
        return airm(scores, weights)
