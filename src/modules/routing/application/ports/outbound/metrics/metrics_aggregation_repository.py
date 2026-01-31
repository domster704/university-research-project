from typing import Protocol


class MetricsAggregationRepository(Protocol):
    def update_cpu(self, node_id: str, value: float) -> None:
        ...

    def update_mem(self, node_id: str, value: float) -> None:
        ...

    def get_averages(self) -> dict[str, dict[str, float]]:
        ...

    def add_latency(self, node_id: str, latency_ms: float) -> None:
        ...