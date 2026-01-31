from typing import Protocol

import numpy as np


class WeightsProvider(Protocol):
    def compute(self, matrix: np.ndarray) -> list[float]:
        ...
