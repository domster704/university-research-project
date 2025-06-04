"""Конфигурационные константы и пороги приложения."""

CPU_THRESHOLD: float = 3.0  # 300 %
MEM_THRESHOLD: float = 0.9  # 90 %
NIC_GBPS: int = 1  # пропускная способность 1 Gb/s
COLLECT_PERIOD: float = 1  # шаг опроса docker stats (сек)
LAT_WINDOW: int = 100  # скольких последних запросов хранить для latency
DEFAULT_ALGORITHM: str = "airm"  # алгоритм по умолчанию

NODE_ENDPOINTS = {
}


def update_node_endpoints(nodes: dict) -> None:
    """Добавляет новые ноды в словарь NODE_ENDPOINTS."""
    for name, addr in nodes.items():
        NODE_ENDPOINTS[name] = ("127.0.0.1", addr)
