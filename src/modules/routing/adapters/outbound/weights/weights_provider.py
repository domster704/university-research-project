from src.modules.mcdm.weights.entropy import entropy_weights
from src.modules.routing.application.ports.outbound.weights.weights_provider import WeightsProvider


class EntropyWeightsProvider(WeightsProvider):
    def compute(self, matrix):
        return entropy_weights(matrix)
