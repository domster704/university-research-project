from src.domain.services.balancer import Balancer
from src.domain.algorithms.topsis import topsis
from src.application.usecases.choose_node_uc import ChooseNodeUseCase

from src.adapters.outbound.metrics.docker_metrics_adapter import DockerMetricsAdapter
from src.adapters.outbound.registry.docker_node_registry import DockerNodeRegistry

def build_choose_node_port():
    metrics = DockerMetricsAdapter()
    registry = DockerNodeRegistry()
    balancer = Balancer(topsis)

    return ChooseNodeUseCase(
        metrics_provider=metrics,
        registry=registry,
        balancer=balancer,
    )
