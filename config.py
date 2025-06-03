"""Конфигурационные константы и пороги приложения."""

CPU_THRESHOLD: float = 0.80  # 80 %
MEM_THRESHOLD: float = 0.80  # 80 %
NIC_GBPS: int = 1  # пропускная способность 1 Gb/s
COLLECT_PERIOD: float = 3.0  # шаг опроса docker stats (сек)
LAT_WINDOW: int = 100  # скольких последних запросов хранить для latency
DEFAULT_ALGORITHM: str = "topsis"  # алгоритм по умолчанию

NODE_ENDPOINTS = {
    "server1": ("127.0.0.1", 8001),
    "server2": ("127.0.0.1", 8002),
    "server3": ("127.0.0.1", 8003),
}
