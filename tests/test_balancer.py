import numpy as np
from balancer import choose_node
from models import NodeMetrics

class DummyCollector:
    def __init__(self, prev): self._prev = prev
    def get_prev(self, node_id): return self._prev


def make_metrics():
    return [NodeMetrics.now_iso(), 'node1', 0.1, 0.2, 0, 0], []