# balancer.py
"""Фасад: агрегирует сбор метрик, веса и алгоритмы."""

from __future__ import annotations

from typing import List

import numpy as np

import config
from algorithms import get_algorithm
from models import NodeMetrics
from weights import entropy_weights


def choose_node(metrics: List[NodeMetrics],
                alg_name: str = config.DEFAULT_ALGORITHM) -> str:
    """Главная точка выбора узла.

    Args:
        metrics: Метрики всех доступных нод.
        alg_name: Имя алгоритма (из algorithms.REGISTRY).

    Returns:
        node_id лучшей ноды.
    """
    # --- отбраковка по порогам --- #
    metrics = [
        m for m in metrics
        if m.cpu_util < config.CPU_THRESHOLD and
           m.mem_util < config.MEM_THRESHOLD
    ]
    if not metrics:
        raise RuntimeError("Все ноды перегружены > 80 %!")

    # --- формируем матрицу решений --- #
    X = np.vstack([m.to_vector() for m in metrics]).astype(float)
    # --- считаем веса --- #
    w = entropy_weights(X)
    # --- применяем алгоритм --- #
    alg = get_algorithm(alg_name)
    best_idx = alg(X, w)
    return metrics[best_idx].node_id
