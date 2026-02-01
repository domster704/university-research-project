import numpy as np

from src.modules.types.numpy import Matrix, Vector


# Время выполнения: 0.006000 секунд
def lc(
        x_matrix: Matrix,
        w: Vector,
) -> int:
    """
    Метод взвешенной суммы (Linear Scalarization).

    Параметры
    ----------
    x_matrix : ndarray (m, n)
        Матрица решений: m альтернатив × n критериев.
    w : 1-D ndarray (n,)
        Номинальный вектор весов критериев. Уже нормирован.

    Возвращает
    ----------
    int
        Индекс (0-based) альтернативы с наибольшей вероятностью доминирования.
    """
    if (w < 0).any():
        raise ValueError("все веса должны быть > 0")

    scores: Vector = x_matrix @ w
    return int(np.argmax(scores))
