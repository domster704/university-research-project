"""Энтропийный метод вычисления весов критериев."""

import numpy as np


def entropy_weights(x_matrix: np.ndarray) -> np.ndarray:
    m, n = x_matrix.shape
    if m == 1:
        return np.full(n, 1.0 / n)

    x_matrix = x_matrix + 1e-12
    p = x_matrix / x_matrix.sum(axis=0, keepdims=True)
    k = 1.0 / np.log(m)

    # Формула Шеннона
    e = (-k) * (p * np.log(p)).sum(axis=0)
    d = 1.0 - e

    d = np.clip(d, 0.0, None)
    return d / d.sum()
