from __future__ import annotations

from collections import defaultdict, deque
from threading import RLock

from src.modules.routing.application.ports.outbound.metrics.metrics_repository import MetricsRepository
from src.modules.routing.domain.entities.node.node_metrics import NodeMetrics


class InMemoryMetricsRepository(MetricsRepository):
    """
    Хранит историю по каждому node_id отдельно.
    prev = предпоследнее значение.
    latest = последнее.
    """

    def __init__(self, history_limit: int = 32):
        self._lock = RLock()
        self._history: dict[str, deque[NodeMetrics]] = defaultdict(lambda: deque(maxlen=history_limit))

    def upsert(self, metrics: NodeMetrics) -> None:
        with self._lock:
            self._history[metrics.node_id].append(metrics)

    def get_latest(self, node_id: str) -> NodeMetrics | None:
        with self._lock:
            h = self._history.get(node_id)
            return h[-1] if h else None

    def get_prev(self, node_id: str) -> NodeMetrics | None:
        with self._lock:
            h = self._history.get(node_id)
            if not h or len(h) < 2:
                return None
            return h[-2]

    def list_latest(self) -> list[NodeMetrics]:
        with self._lock:
            out: list[NodeMetrics] = []
            for h in self._history.values():
                if h:
                    out.append(h[-1])
            return out
