# weights.py
"""Энтропийный метод вычисления весов критериев."""

from __future__ import annotations

import numpy as np


def entropy_weights(x_matrix: np.ndarray) -> np.ndarray:
    """Энтропийные веса с учётом m == 1."""
    m, n = x_matrix.shape
    if m == 1:
        # Одна альтернатива → все веса одинаковые
        return np.full(n, 1.0 / n)

    x_matrix = x_matrix + 1e-12
    p = x_matrix / x_matrix.sum(axis=0, keepdims=True)
    k = 1.0 / np.log(m)
    e = (-k) * (p * np.log(p)).sum(axis=0)  # энтропия
    d = 1.0 - e
    return d / d.sum()
