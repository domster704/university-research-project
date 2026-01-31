from collections import defaultdict
from typing import DefaultDict

from old.models import NodeMetrics

_cpu_sum: DefaultDict[str, float] = defaultdict(float)
_cpu_cnt: DefaultDict[str, int] = defaultdict(int)

_mem_sum: DefaultDict[str, float] = defaultdict(float)
_mem_cnt: DefaultDict[str, int] = defaultdict(int)

_cpu_avg: dict[str, float] = defaultdict(float)
_mem_avg: dict[str, float] = defaultdict(float)

ALPHA = 0.3


def _ema(prev: float, cur: float, alpha: float = ALPHA) -> float:
    return cur if prev == 0 else alpha * cur + (1 - alpha) * prev


def update_resources(port: str,
                     cpu: float | None = None,
                     mem: float | None = None) -> None:
    """Обновляем EMA-среднее: игнорируем None-поля."""
    if cpu is not None:
        _cpu_avg[port] = _ema(_cpu_avg[port], cpu)
    if mem is not None:
        _mem_avg[port] = _ema(_mem_avg[port], mem)


def get_avg_resources() -> dict[str, dict[str, float]]:
    """Возвращает средние CPU/RAM по каждому порту."""
    return {
        "cpu_avg_percentage": _cpu_avg,
        "mem_avg_percentage": _mem_avg,
    }


def update_resources_by_metrics(metrics_dict: dict[str, NodeMetrics], url_path: str, port: int) -> None:
    for node_name, node_metrics in metrics_dict.items():
        if node_metrics:
            if url_path.startswith("/cpu"):
                update_resources(str(port), cpu=node_metrics.cpu_util)
            elif url_path.startswith("/mem"):
                update_resources(str(port), mem=node_metrics.mem_util)
