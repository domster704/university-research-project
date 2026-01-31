import numpy as np

from src.modules.routing.application.ports.inbound.node.choose_node_port import ChooseNodePort
from src.modules.routing.application.ports.outbound.metrics.metrics_repository import MetricsRepository
from src.modules.routing.application.ports.outbound.node.node_registry import NodeRegistry
from src.modules.routing.application.ports.outbound.weights.weights_provider import WeightsProvider
from src.modules.routing.config.settings import settings


class ChooseNodeUseCase(ChooseNodePort):
    def __init__(
            self,
            repo: MetricsRepository,
            registry: NodeRegistry,
            weights: WeightsProvider,
            strategy,
    ):
        self.repo = repo
        self.registry = registry
        self.weights = weights
        self.strategy = strategy

    async def execute(self) -> tuple[str, int]:
        metrics = self.repo.list_latest()
        if not metrics:
            raise RuntimeError("Нет метрик: коллектор ещё не собрал данные")

        vectors = [
            m.to_vector(
                interval=settings.collector_interval,
                prev=self.repo.get_prev(m.node_id)
            )
            for m in metrics
        ]

        X: np.ndarray = np.vstack(vectors).astype(float)
        w: list[float] = self.weights.compute(X)

        idx: int = self.strategy.choose(X, w)
        return metrics[idx].node_id, idx
