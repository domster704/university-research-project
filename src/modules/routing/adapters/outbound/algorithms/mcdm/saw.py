from src.modules.mcdm.algorithms.saw import saw
from src.modules.routing.domain.policies.ranking_strategy import RankingStrategy
from src.modules.types.numpy import Matrix, Vector


class SAWStrategy(RankingStrategy):
    def choose(self, scores: Matrix, weights: Vector) -> int:
        return saw(scores, weights)
