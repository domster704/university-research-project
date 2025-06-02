# algorithms/saw.py
"""SAW (Simple Additive Weighting) c энтропийными весами."""

from __future__ import annotations

import numpy as np


def saw(x_matrix: np.ndarray, w: np.ndarray) -> int:
    """Возвращает индекс лучшего варианта.

    Args:
        x_matrix: Матрица решений.
        w: Вектор весов.

    Returns:
        Индекс строки-победителя.
    """
    # Все критерии – «издержки»: меньше → лучше.
    R = x_matrix.min(axis=0) / (x_matrix + 1e-12)
    scores = (R * w).sum(axis=1)
    return int(np.argmax(scores))
