from src.modules.routing.adapters.outbound.algorithms.mcdm.saw import SawStrategy
from src.modules.routing.adapters.outbound.algorithms.mcdm.topsis import TopsisStrategy


class AlgorithmRegistry:
    def __init__(self):
        self._algos = {
            "topsis": TopsisStrategy(),
            "saw": SawStrategy(),
        }

    def get(self, name: str):
        try:
            return self._algos[name]
        except KeyError:
            raise ValueError(f"Unknown algorithm: {name}")
