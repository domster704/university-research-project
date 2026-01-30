from src.application.ports.outbound.metrics_provider import MetricsProvider
from src.domain.models.node_metrics import NodeMetrics


class DockerMetricsAdapter(MetricsProvider):
    async def get_current(self) -> list[NodeMetrics]:
        # здесь твой aiodocker
        return [
            NodeMetrics("svc_a", 0.3, 0.4, 0.1),
            NodeMetrics("svc_b", 0.6, 0.2, 0.3),
        ]
