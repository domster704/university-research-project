# weights.py
"""Энтропийный метод вычисления весов критериев."""

from __future__ import annotations

import numpy as np


def entropy_weights(x_matrix: np.ndarray) -> np.ndarray:
    """Считает веса критериев по энтропийному принципу.

    Args:
        x_matrix: Матрица решений (m вариантов × n критериев).

    Returns:
        Вектор весов w длиной n, сумма = 1.
    """
    x_matrix = x_matrix + 1e-12  # избегаем log(0)
    P = x_matrix / x_matrix.sum(axis=0, keepdims=True)
    E = (-1 / np.log(len(x_matrix))) * (P * np.log(P)).sum(axis=0)
    d = 1.0 - E
    return d / d.sum()
