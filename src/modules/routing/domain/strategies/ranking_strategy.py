from typing import Protocol

import numpy as np


class RankingStrategy(Protocol):
    def choose(self, scores: np.ndarray, weights: np.ndarray) -> int:
        ...
