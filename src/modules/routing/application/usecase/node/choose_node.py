import numpy as np

from src.modules.routing.application.ports.inbound.node.choose_node_port import (
    ChooseNodePort,
)
from src.modules.routing.application.ports.outbound.metrics.metrics_repository import (
    MetricsRepository,
)
from src.modules.routing.application.ports.outbound.node.node_registry import (
    NodeRegistry,
)
from src.modules.routing.application.ports.outbound.weights.weights_provider import (
    WeightsProvider,
)
from src.modules.routing.config.settings import settings
from src.modules.routing.domain.entities.node.node_metrics import NodeMetrics
from src.modules.types.numpy import Vector, Matrix


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

    async def execute(self) -> tuple[str, str, int]:
        metrics: list[NodeMetrics] = self.repo.list_latest()
        if not metrics:
            raise RuntimeError("Нет метрик: коллектор ещё не собрал данные")

        vectors: list[list[float]] = [
            m.to_vector(
                interval=settings.collector_interval, prev=self.repo.get_prev(m.node_id)
            )
            for m in metrics
        ]

        X: Matrix = np.vstack(vectors).astype(float)
        w: Vector = self.weights.compute(X)

        chosen_idx: int = self.strategy.choose(X, w)
        chosen_node: NodeMetrics = metrics[chosen_idx]
        host, port = self.registry.get_endpoint(chosen_node.node_id)

        return chosen_node.node_id, host, port
