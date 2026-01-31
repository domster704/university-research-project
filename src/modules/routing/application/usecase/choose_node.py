import numpy as np

from src.modules.routing.application.ports.inbound.node.choose_node_port import ChooseNodePort
from src.modules.routing.application.ports.outbound.metrics.metrics_history import MetricsHistory
from src.modules.routing.application.ports.outbound.metrics.metrics_provider import MetricsProvider
from src.modules.routing.application.ports.outbound.weights.weights_provider import WeightsProvider
from src.modules.routing.config.settings import settings
from src.modules.routing.domain.services.balancer import Balancer


class ChooseNodeUseCase(ChooseNodePort):
    def __init__(
            self,
            metrics_provider: MetricsProvider,
            history: MetricsHistory,
            weights: WeightsProvider,
            balancer: Balancer,
    ):
        self.metrics_provider = metrics_provider
        self.history = history
        self.weights = weights
        self.balancer = balancer

    async def execute(self) -> tuple[str, int]:
        metrics = await self.metrics_provider.get_current()
        if not metrics:
            raise RuntimeError("Нет метрик")

        vectors = [
            m.to_vector(
                interval=settings.collector_interval,
                prev=self.history.get_prev(m.node_id)
            )
            for m in metrics
        ]

        X = np.vstack(vectors).astype(float)
        w = self.weights.compute(X)

        idx: int = self.balancer.choose(X, w)
        return metrics[idx].node_id, idx
