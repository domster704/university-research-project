# algorithms/nsga2.py
"""Минимальная реализация NSGA-II под задачу «минимизировать max»."""

from __future__ import annotations

import random

import numpy as np

_POP = 16
_GEN = 8
_CROSS_P = 0.9
_MUT_P = 0.2


def _crowding_sort(pop, fitnesses):
    """Быстрая нестрогая сортировка по фронтам + crowding distance."""
    fronts = [[]]
    S = [[] for _ in pop]
    n = [0] * len(pop)

    for p, fp in enumerate(fitnesses):
        for q, fq in enumerate(fitnesses):
            if all(fp <= fq) and any(fp < fq):
                S[p].append(q)
            elif all(fq <= fp) and any(fq < fp):
                n[p] += 1
        if n[p] == 0:
            fronts[0].append(p)

    i = 0
    while fronts[i]:
        next_f = []
        for p in fronts[i]:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    next_f.append(q)
        i += 1
        fronts.append(next_f)

    # crowding distance
    dist = [0.0] * len(pop)
    for front in fronts[:-1]:
        fvals = np.array([fitnesses[i] for i in front])
        for j in range(fvals.shape[1]):
            order = fvals[:, j].argsort()
            dist[front[order[0]]] = dist[front[order[-1]]] = float("inf")
            span = fvals[order[-1], j] - fvals[order[0], j] + 1e-12
            for k in range(1, len(front) - 1):
                i1, i2 = front[order[k - 1]], front[order[k + 1]]
                dist[front[order[k]]] += (fvals[i2, j] - fvals[i1, j]) / span
    return fronts, dist


def nsga2_minmax(x_matrix: np.ndarray, _w_unused=None) -> int:
    """NSGA-II: ищем вектор весов, минимизирующий max критериев.

    Args:
        x_matrix: Матрица решений (m×n).
        _w_unused: 

    Returns:
        Индекс лучшей альтернативы (min max).
    """
    m, n = x_matrix.shape
    pop = [np.random.dirichlet(np.ones(n)) for _ in range(_POP)]

    for _ in range(_GEN):
        # ---------- оценка ---------- #
        fitnesses = [((p * x_matrix).sum(axis=1).max(),) for p in pop]
        # ---------- сортировка ---------- #
        fronts, crowd = _crowding_sort(pop, fitnesses)
        # ---------- селекция ---------- #
        new_pop = []
        for front in fronts:
            if len(new_pop) + len(front) > _POP:
                break
            new_pop.extend(front)
        while len(new_pop) < _POP:
            a, b = random.sample(fronts[0], 2)
            new_pop.append(a if crowd[a] > crowd[b] else b)
        pop = [pop[i] for i in new_pop]

        # ---------- оператор скрещивания ---------- #
        offspring = []
        for _ in range(_POP // 2):
            if random.random() < _CROSS_P:
                p1, p2 = random.sample(pop, 2)
                alpha = random.random()
                c1 = alpha * p1 + (1 - alpha) * p2
                c2 = (1 - alpha) * p1 + alpha * p2
                offspring += [c1 / c1.sum(), c2 / c2.sum()]
        pop.extend(offspring)

        # ---------- мутация ---------- #
        for i in range(len(pop)):
            if random.random() < _MUT_P:
                j = random.randrange(n)
                pop[i][j] = max(pop[i][j] + np.random.normal(0, 0.1), 1e-3)
                pop[i] /= pop[i].sum()

        # обрезаем
        pop = pop[:_POP]

    # финальный выбор: веса → оценка → argmin max
    best_weights = min(pop, key=lambda w: (w * x_matrix).sum(axis=1).max())
    scores = (best_weights * x_matrix).sum(axis=1)
    return int(np.argmin(scores))
