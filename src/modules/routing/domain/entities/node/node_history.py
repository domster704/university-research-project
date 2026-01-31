from old.models import NodeMetrics


class NodeHistory:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.records: list[NodeMetrics] = []

    def add(self, metrics: NodeMetrics):
        self.records.append(metrics)

    def last(self) -> NodeMetrics | None:
        return self.records[-1] if self.records else None
