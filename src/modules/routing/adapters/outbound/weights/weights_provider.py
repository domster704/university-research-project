from src.modules.mcdm.weights.entropy import entropy_weights
from src.modules.routing.application.ports.outbound.weights.weights_provider import (
    WeightsProvider,
)
from src.modules.types.numpy import Matrix, Vector


class EntropyWeightsProvider(WeightsProvider):
    def compute(self, matrix: Matrix) -> Vector:
        return entropy_weights(matrix)
