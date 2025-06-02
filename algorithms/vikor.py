# algorithms/vikor.py
"""VIKOR (вариация рациональности)."""

from __future__ import annotations

import numpy as np


def vikor(x_matrix: np.ndarray, w: np.ndarray, v: float = 0.5) -> int:
    """Индекс лучшего варианта методом VIKOR.

    Args:
        x_matrix: Матрица решений.
        w: Вектор весов.
        v: Коэффициент компромисса (0–1).

    Returns:
        Индекс строки-победителя.
    """
    f_best = x_matrix.min(axis=0)
    f_worst = x_matrix.max(axis=0)
    S = ((w * (x_matrix - f_best) / (f_worst - f_best)).sum(axis=1))
    R = ((w * (x_matrix - f_best) / (f_worst - f_best)).max(axis=1))
    S_best, S_worst = S.min(), S.max()
    R_best, R_worst = R.min(), R.max()
    Q = v * (S - S_best) / (S_worst - S_best + 1e-12) + \
        (1 - v) * (R - R_best) / (R_worst - R_best + 1e-12)
    return int(np.argmin(Q))
