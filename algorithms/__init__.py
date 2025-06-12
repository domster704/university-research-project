"""Реестр всех алгоритмов многокритериального выбора."""

from __future__ import annotations

from .airm import airm
from .electre import electre
from .saw import saw
from .topsis import topsis
from .lc import lc

REGISTRY = {
    "saw": saw,
    "topsis": topsis,
    "electre": electre,
    "airm": airm,
    "lc": lc,
}


def get_algorithm(name: str):
    """Возвращает функцию-алгоритм по имени или кидает ValueError."""
    try:
        return REGISTRY[name.lower()]
    except KeyError as exc:
        raise ValueError(f"Неизвестный алгоритм: {name}") from exc


if __name__ == "__main__":
    import numpy as np
    from weights import entropy_weights


    X = np.array([[90, 30, 0.1],
                  [3, 40, 0.1],
                  [15, 3, 2]])
    w = entropy_weights(X)
    print(w)

    # for _ in range(5):
    #     saw(X, w)
