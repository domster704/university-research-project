from src.modules.routing.adapters import DockerMetricsAdapter
from src.modules.routing.adapters import DockerNodeRegistry
from src.modules.routing.application import ChooseNodeUseCase
from src.modules.routing.domain import topsis

from src.modules.routing.domain.services.balancer import Balancer


def build_choose_node_port() -> ChooseNodeUseCase:
    metrics = DockerMetricsAdapter()
    registry = DockerNodeRegistry()
    balancer = Balancer(topsis)

    return ChooseNodeUseCase(
        metrics_provider=metrics,
        registry=registry,
        balancer=balancer,
    )
