import numpy as np

from src.modules.types.numpy import Matrix, Vector, BoolVector, IntVector


# Время выполнения: 0.006000 секунд
def airm(
        x_matrix: Matrix,
        w: Vector,
        *,
        n_iter: int = 1000,
        alpha_scale: float = 5,
        benefit_mask=None,
        random_state: int | None = None,
) -> int:
    """
    Метод рандомизации агрегированных индексов (AIRM).

    Параметры
    ----------
    x_matrix : ndarray (m, n)
        Матрица решений: m альтернатив × n критериев.
    w : 1-D ndarray (n,)
        Номинальный вектор весов критериев.
    n_iter : int, default 10000
        Число Монте-Карло итераций (чем больше, тем стабильнее результат).
    alpha_scale : float, default 100.0
        Масштаб параметров α для распределения Дирихле:
        α_j = w_j × alpha_scale. Большое значение ⇒ веса колеблются
        ближе к номинальным, маленькое — более «плоское» распределение.
    benefit_mask : 1-D ndarray (n,), optional
        Логический вектор: True — критерий «выгоды» (больше = лучше),
        False — «затрат» (меньше = лучше). По умолчанию все критерии выгоды.
    random_state : int, optional
        Зёрно генератора случайных чисел для воспроизводимости.

    Возвращает
    ----------
    int
        Индекс (0-based) альтернативы с наибольшей вероятностью доминирования.
    """
    if (w < 0).any():
        raise ValueError("все веса должны быть > 0")

    if benefit_mask is None:
        benefit_mask = np.zeros(len(w), dtype=bool)

    rng = np.random.default_rng(random_state)
    x: Matrix = np.asarray(x_matrix, dtype=float)
    m, n = x.shape

    benefit_mask: BoolVector = np.asarray(benefit_mask, dtype=bool)
    if benefit_mask.shape != (n,):
        raise ValueError("benefit_mask должен иметь длину n")

    # приведение всех критериев к «выгода»
    x_adj: Matrix = x.copy()
    # для затратных: чем меньше, тем лучше ⇒ инвертируем
    if (~benefit_mask).any():
        x_adj[:, ~benefit_mask] = x_adj[:, ~benefit_mask].max(axis=0) - x_adj[:, ~benefit_mask]

    # масштабирование столбцов в [0, 1]
    col_min: Vector = x_adj.min(axis=0)
    col_max: Vector = x_adj.max(axis=0)
    denominator: Vector = np.where(col_max == col_min, 1.0, col_max - col_min)
    x_norm: Matrix = (x_adj - col_min) / denominator

    # рандомизация весов и подсчёт побед
    counts: IntVector = np.zeros(m, dtype=int)
    alpha: Vector = w * alpha_scale

    for _ in range(n_iter):
        w_rand: Vector = rng.dirichlet(alpha)
        scores: Vector = x_norm @ w_rand  # агрегированный индекс
        counts[scores.argmax()] += 1  # победитель этой итерации

    return int(counts.argmax())
