"""Модели данных и вспомогательные функции."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

import numpy as np

from config import COLLECT_PERIOD


@dataclass
class NodeMetrics:
    """Снимок показателей одной Docker-ноды.

    Attributes:
        timestamp: ISO-8601 время метки.
        node_id: Идентификатор узла (IP или hostname).
        cpu_util: Загрузка CPU в долях (0–1).
        mem_util: Загрузка памяти в долях (0–1).
        net_in_bytes: Принятые байты с момента старта контейнера.
        net_out_bytes: Отправленные байты с момента старта.
        latency_ms: Средняя задержка (скользящее окно) или None.
    """
    timestamp: str
    node_id: str
    cpu_util: float
    mem_util: float
    net_in_bytes: int
    net_out_bytes: int
    latency_ms: float | None = None

    # ---------- агрегаторы ---------- #

    def to_vector(self,
                  prev: NodeMetrics | None = None,
                  interval: float = COLLECT_PERIOD,
                  nic_gbps: int = 1) -> List[float]:
        """Преобразует метрику в числовой вектор для MCDM.

        Args:
            prev: Предыдущий снимок той же ноды.
            interval: Шаг измерения (секунды).
            nic_gbps: Пропускная способность сетевого интерфейса.

        Returns:
            Вектор [cpu_util, mem_util, net_util] в диапазоне [0,1].
        """
        cpu = self.cpu_util
        mem = self.mem_util

        # --- считаем сетевую активность как Δбайт/с --- #
        if prev:
            delta_in = self.net_in_bytes - prev.net_in_bytes
            delta_out = self.net_out_bytes - prev.net_out_bytes
            net_Bps = max(delta_in, delta_out) / max(interval, 1e-6)
        else:
            net_Bps = 0.0
        nic_Bps = nic_gbps * 125_000_000  # 1 Gb/s = 125 MB/s
        net_util = min(net_Bps / nic_Bps, 1.0)  # clamp в [0,1]

        return [cpu, mem, net_util]

    @staticmethod
    def now_iso() -> str:
        """Текущее время в ISO-8601."""
        return datetime.now(timezone.utc).isoformat()
