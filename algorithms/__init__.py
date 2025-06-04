"""Реестр всех алгоритмов многокритериального выбора."""

from __future__ import annotations

from .airm import airm
from .electre import electre
from .saw import saw
from .topsis import topsis

REGISTRY = {
    "saw": saw,
    "topsis": topsis,
    "electre": electre,
    "airm": airm,
}


def get_algorithm(name: str):
    """Возвращает функцию-алгоритм по имени или кидает ValueError."""
    try:
        return REGISTRY[name.lower()]
    except KeyError as exc:
        raise ValueError(f"Неизвестный алгоритм: {name}") from exc
