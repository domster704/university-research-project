from src.modules.mcdm.algorithms.electre import electre
from src.modules.routing.domain.policies.ranking_strategy import RankingStrategy
from src.modules.types.numpy import Matrix, Vector


class ELECTREStrategy(RankingStrategy):
    def choose(self, scores: Matrix, weights: Vector) -> int:
        return electre(scores, weights)
