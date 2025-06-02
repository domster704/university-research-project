# algorithms/topsis.py
"""TOPSIS с «издержковыми» критериями."""

from __future__ import annotations

import numpy as np


def topsis(x_matrix: np.ndarray, w: np.ndarray) -> int:
    """Индекс лучшего варианта методом TOPSIS."""
    # 1) нормируем (векторная норма)
    R = x_matrix / np.linalg.norm(x_matrix, axis=0)
    # 2) взвешиваем
    V = R * w
    # 3) определяем идеальные/анти-идеальные точки
    A_pos = V.min(axis=0)  # cost → min лучше
    A_neg = V.max(axis=0)
    # 4) считаем расстояния
    D_pos = np.linalg.norm(V - A_pos, axis=1)
    D_neg = np.linalg.norm(V - A_neg, axis=1)
    C = D_neg / (D_pos + D_neg)
    return int(np.argmax(C))
