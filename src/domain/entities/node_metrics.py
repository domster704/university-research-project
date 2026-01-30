from dataclasses import dataclass


@dataclass(frozen=True)
class NodeMetrics:
    node_id: str
    cpu_util: float
    mem_util: float
    net_util: float
    latency_ms: float | None
