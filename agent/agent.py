import asyncio

import aiodocker
import aiohttp

from models import NodeMetrics
from .config import AGENT_ID, SERVER_URL, COLLECT_PERIOD


async def collect_and_send():
    docker = aiodocker.Docker()
    async with aiohttp.ClientSession() as session:
        while True:
            containers = await docker.containers.list()
            metrics = []

            for c in containers:
                stats = await c.stats(stream=False)
                # CPU %
                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                            stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                               stats["precpu_stats"]["system_cpu_usage"]
                online_cpus = stats["cpu_stats"].get("online_cpus", 1)
                cpu_util = cpu_delta / (system_delta + 1e-12) * online_cpus

                # MEM %
                mem_util = stats["memory_stats"]["usage"] / stats["memory_stats"]["limit"]

                # NET bytes
                networks = stats.get("networks", {})
                net_in = sum(n["rx_bytes"] for n in networks.values()) if networks else 0
                net_out = sum(n["tx_bytes"] for n in networks.values()) if networks else 0

                # Формируем NodeMetrics
                nm = NodeMetrics(
                    timestamp=NodeMetrics.now_iso(),
                    node_id=c.id,
                    cpu_util=float(cpu_util),
                    mem_util=float(mem_util),
                    net_in_bytes=int(net_in),
                    net_out_bytes=int(net_out),
                )
                metrics.append(nm)

            # Отправляем на сервер
            payload = {
                'agent_id': AGENT_ID,
                'metrics': [m._asdict() for m in metrics]
            }
            try:
                await session.post(f"{SERVER_URL}/metrics", json=payload)
            except Exception as e:
                print(f"Ошибка отправки метрик: {e}")

            await asyncio.sleep(COLLECT_PERIOD)


if __name__ == '__main__':
    asyncio.run(collect_and_send())

"""
Agent send to balancer HOST:

POST /metrics
{
  "agent_id": "имя-хоста-или-uuid",
  "metrics": [
    {
      "timestamp": "...",
      "node_id": "...",
      "cpu_util": 0.12,
      "mem_util": 0.34,
      "net_in_bytes": 12345,
      "net_out_bytes": 6789
    },
    ...
  ]
}
"""

"""Удалённый Docker API — это тот же REST‑интерфейс (Engine API), который Docker‑демон предоставляет локальному клиенту `docker`, но доступный по сети. По умолчанию Docker слушает только UNIX‑сокет (`/var/run/docker.sock`), но его можно заставить слушать TCP‑порт (обычно 2375 или 2376) и тогда вы можете управлять контейнерами на удалённой машине так же, как на локальной.

---

### Как это работает

1. **Docker Engine API**
   Docker‑демон («`dockerd`») реализует HTTP‑API, описанное в спецификации Engine API (см. документацию Docker). Клиент (CLI или ваша программа) отправляет HTTP‑запросы на эндпоинты вроде:

   * `GET /containers/json` — список контейнеров
   * `GET /containers/{id}/stats` — статистика по одному контейнеру
   * `POST /containers/{id}/start` и т.п.

2. **Настройка слушателя TCP**
   По умолчанию в Ubuntu или Debian в `/etc/docker/daemon.json` в секции `"hosts"`:

   ```json
   {
     "hosts": ["unix:///var/run/docker.sock"]
   }
   ```

   Чтобы включить TCP‑доступ, добавьте, например:

   ```json
   {
     "hosts": [
       "unix:///var/run/docker.sock",
       "tcp://0.0.0.0:2376"
     ]
   }
   ```

   После перезапуска `systemctl restart docker` демон начнёт слушать порт 2376 на всех интерфейсах.

3. **Безопасность: TLS**
   Открывать Docker без TLS опасно — любой, кто попадёт на порт 2376, получит полный контроль над контейнерами и хостом. Поэтому для production‑системы обычно настраивают TLS‑сертификаты:

   ```json
   {
     "hosts": ["unix:///var/run/docker.sock","tcp://0.0.0.0:2376"],
     "tls": true,
     "tlsverify": true,
     "tlscacert": "/etc/docker/certs/ca.pem",
     "tlscert": "/etc/docker/certs/server-cert.pem",
     "tlskey": "/etc/docker/certs/server-key.pem"
   }
   ```

   Клиентам (вашему агенту или другим хостам) понадобится копия CA‑сертификата и client‑cert/key.

4. **Пример подключения из Python**
   С библиотекой `aiodocker` (или `docker-py`) вы можете задать переменную окружения:

   ```bash
   export DOCKER_HOST="tcp://docker.example.com:2376"
   export DOCKER_TLS_VERIFY="1"
   export DOCKER_CERT_PATH="/home/user/.docker/certs"
   ```

   Или явно в коде:

   ```python
   import aiodocker
   import ssl

   ssl_ctx = ssl.create_default_context(
       cafile="/path/to/ca.pem"
   )
   ssl_ctx.load_cert_chain(
       certfile="/path/to/cert.pem",
       keyfile="/path/to/key.pem"
   )

   docker = aiodocker.Docker(url="https://docker.example.com:2376", ssl=ssl_ctx)
   containers = await docker.containers.list()
   ```

5. **Плюсы и минусы**

   * **Без агента**: не нужно разворачивать дополнительный код‑агент, ваша логика просто подключается к Docker‑демону по сети.
   * **С TLS**: требуется управление сертификатами, чуть более сложная настройка.
   * **Сеть**: Docker‑демон открывает порт, возможно, через фаервол надо будет открывать/перенаправлять.
   * **Агент**: можно запускать в контейнере рядом с другими сервисами, сложность TLS не требуется, зато есть дополнительный слой кода.

---

**Итого:**
Удалённый Docker API — это просто сетевой доступ к тому же интерфейсу управления контейнерами, что и локальный `docker`. Если вам удобно настраивать и поддерживать TLS-сертификаты, можно сразу подключаться к демону по TCP и собирать метрики без отдельного агента. Если же вы хотите упростить безопасность и не открывать демон в сеть, лучше использовать лёгкий агент рядом с Docker‑сокетом.
"""
