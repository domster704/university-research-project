from __future__ import annotations

import numpy as np


# Время выполнения: 0.006000 секунд
def airm(
        x_matrix: np.ndarray,
        w: np.ndarray,
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
        benefit_mask = [False, False, False]

    rng = np.random.default_rng(random_state)
    x = np.asarray(x_matrix, dtype=float)
    m, n = x.shape

    benefit_mask = np.asarray(benefit_mask, dtype=bool)
    if benefit_mask.shape != (n,):
        raise ValueError("benefit_mask должен иметь длину n")

    # --- приведение всех критериев к «выгода» ---------------
    x_adj = x.copy()
    # для затратных: чем меньше, тем лучше ⇒ инвертируем
    if (~benefit_mask).any():
        x_adj[:, ~benefit_mask] = x_adj[:, ~benefit_mask].max(axis=0) - x_adj[:, ~benefit_mask]

    # --- масштабирование столбцов в [0, 1] ------------------
    col_min = x_adj.min(axis=0)
    col_max = x_adj.max(axis=0)
    denom = np.where(col_max == col_min, 1.0, col_max - col_min)
    x_norm = (x_adj - col_min) / denom

    # --- рандомизация весов и подсчёт побед -----------------
    counts = np.zeros(m, dtype=int)
    alpha = w * alpha_scale

    for _ in range(n_iter):
        w_rand = rng.dirichlet(alpha)
        scores = x_norm @ w_rand  # агрегированный индекс
        counts[scores.argmax()] += 1  # победитель этой итерации

    print(counts)

    return int(counts.argmax())