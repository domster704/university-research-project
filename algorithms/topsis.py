from __future__ import annotations

import numpy as np


# Время выполнения: 0.000999450684 секунд
def topsis(x_matrix: np.ndarray, w: np.ndarray) -> int:
    """Возвращает индекс лучшего варианта методом TOPSIS (все критерии – это издержки)"""
    # 1) нормируем (векторная норма)
    norm = np.linalg.norm(x_matrix, axis=0)
    norm[norm == 0] = 1.0  # чтобы не делить на 0, если столбец нулевой
    R = x_matrix / norm

    # 2) взвешиваем
    V = R * w

    # 3) идеальная и анти-идеальная точки (для «cost» критериев: чем меньше, тем лучше)
    A_pos = V.min(axis=0)  # идеальная (минимум)
    A_neg = V.max(axis=0)  # анти-идеальная (максимум)

    # 4) расстояния до идеальных точек
    D_pos = np.linalg.norm(V - A_pos, axis=1)
    D_neg = np.linalg.norm(V - A_neg, axis=1)

    # 5) относительная близость к идеалу
    denominator = D_pos + D_neg
    C = np.divide(D_neg, denominator, out=np.zeros_like(denominator), where=denominator != 0)

    # 6) индекс наилучшего варианта
    return int(np.argmax(C))
