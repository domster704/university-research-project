from collections import defaultdict

from src.modules.routing.domain.policies.ema import ema


class InMemoryMetricsAggregationRepository:
    def __init__(self, alpha: float = 0.3):
        self.alpha = alpha
        self._cpu_avg = defaultdict(float)
        self._mem_avg = defaultdict(float)

    def update_cpu(self, node_id: str, value: float):
        self._cpu_avg[node_id] = ema(self._cpu_avg[node_id], value, self.alpha)

    def update_mem(self, node_id: str, value: float):
        self._mem_avg[node_id] = ema(self._mem_avg[node_id], value, self.alpha)

    def get_averages(self):
        return {
            "cpu_avg_percentage": dict(self._cpu_avg),
            "mem_avg_percentage": dict(self._mem_avg),
        }
