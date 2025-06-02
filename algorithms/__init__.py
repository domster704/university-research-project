# algorithms/__init__.py
"""Реестр всех алгоритмов многокритериального выбора."""

from __future__ import annotations

from .electre import electre
from .nsga2 import nsga2_minmax
from .saw import saw
from .topsis import topsis
from .vikor import vikor

REGISTRY = {
    "saw": saw,
    "topsis": topsis,
    "vikor": vikor,
    "electre": electre,
    "nsga2": nsga2_minmax,
}


def get_algorithm(name: str):
    """Возвращает функцию-алгоритм по имени или кидает ValueError."""
    try:
        return REGISTRY[name.lower()]
    except KeyError as exc:
        raise ValueError(f"Неизвестный алгоритм: {name}") from exc
