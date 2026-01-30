from src.application.ports.inbound.choose_node_port import ChooseNodePort
from src.application.ports.outbound.metrics_provider import MetricsProvider
from src.application.ports.outbound.node_registry import NodeRegistry
from src.domain.services.balancer import Balancer


class ChooseNodeUseCase(ChooseNodePort):
    def __init__(
            self,
            metrics_provider: MetricsProvider,
            registry: NodeRegistry,
            balancer: Balancer,
    ):
        self.metrics_provider = metrics_provider
        self.registry = registry
        self.balancer = balancer

    async def execute(self) -> tuple[str, int]:
        metrics = await self.metrics_provider.get_current()
        node_id = self.balancer.choose(metrics)
        return self.registry.get_endpoint(node_id)
