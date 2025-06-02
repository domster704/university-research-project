# algorithms/electre.py
"""Упрощённый ELECTRE III для online-использования."""

from __future__ import annotations

import numpy as np

_CONC_THRESHOLD = 0.6  # порог согласия
_DIS_THRESHOLD = 0.4  # порог несогласия


def electre(x_matrix: np.ndarray, w: np.ndarray) -> int:
    """Индекс лучшего варианта по ELECTRE III (упрощённо)."""
    m, n = x_matrix.shape
    concordance = np.zeros((m, m))
    discordance = np.zeros((m, m))

    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            # согласие: сумма весов, где i не хуже j
            mask = x_matrix[i] <= x_matrix[j]  # cost-критерий
            concordance[i, j] = w[mask].sum()
            # несогласие: макс относительного проигрыша
            diff = (x_matrix[i] - x_matrix[j]) / (x_matrix.max(axis=0) - x_matrix.min(axis=0) + 1e-12)
            discordance[i, j] = diff.max()

    outrank = (concordance >= _CONC_THRESHOLD) & (discordance <= _DIS_THRESHOLD)
    # считаем число «побеждённых» каждой альтернативой
    scores = outrank.sum(axis=1)
    return int(np.argmax(scores))
