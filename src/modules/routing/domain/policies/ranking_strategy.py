from typing import Protocol

from src.modules.types.numpy import Matrix, Vector


class RankingStrategy(Protocol):
    def choose(self, scores: Matrix, weights: Vector) -> int: ...
