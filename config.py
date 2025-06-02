"""Конфигурационные константы и пороги приложения."""

CPU_THRESHOLD: float = 0.80         # 80 %
MEM_THRESHOLD: float = 0.80         # 80 %
NIC_GBPS: int = 1                   # пропускная способность 1 Gb/s
COLLECT_PERIOD: float = 2.0         # шаг опроса docker stats (сек)
LAT_WINDOW: int = 100               # скольких последних запросов хранить для latency
DEFAULT_ALGORITHM: str = "topsis"   # алгоритм по умолчанию
