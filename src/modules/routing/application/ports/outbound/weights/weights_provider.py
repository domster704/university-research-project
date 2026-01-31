from typing import Protocol


class WeightsProvider(Protocol):
    def compute(self, matrix) -> list[float]:
        ...
