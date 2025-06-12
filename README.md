# Что надо сделать потом?

## Что у нас есть?

| Компонент                                             | Роль в системе                                                                     |
|-------------------------------------------------------|------------------------------------------------------------------------------------|
| **proxy/app.py**                                      | Принимает запрос, выбирает Docker-нод по MCDM-алгоритму и проксирует дальше.       |
| **collector.py**                                      | Раз в `COLLECT_PERIOD` собирает `docker stats`, формирует `NodeMetrics`.           |
| **balancer.py + algorithms/**                         | Считают весовые коэффициенты (энтропия) и ранжируют ноды (TOPSIS, ELECTRE и т.д.). |
| **test\_server/** + `docker-compose_test-servers.yml` | Локальная распределённая система из 12 контейнеров-заглушек.                       |

### Заметки из чата с Курочкиным И.И.

* Репликация «заказчик ⇄ оператор»
* Вероятность отказа узлов → нужно дублировать (quorum + 1 копия).
* Сначала накапливаем ошибки, потом для них делаем реплики.
* Дедлайны (SLA) и «кол-во задач < хостов» => можно временно гасить лишние контейнеры.
* Жадный алгоритм: на каждом шаге кладём следующую задачу туда, где прирост **максимально** уменьшает оба критерия.

---

## Алгоритм репликации (draft)

> ***Вход:***
> - очередь задач **Q**
> - оценка *p<sub>fail</sub>(node)* для каждой ноды
> - максимальный k-ворум
> - дедлайн *D* (ms).
>
> ***Выход:*** план размещения *(task, replica\_i → node\_j)*.

1. **Оценка риска**
   Для каждой ноды `n` рассчитываем *R(n) = p<sub>fail</sub>(n) × E\[T(n)]*, где `E[T]` — прогноз времени ответа (из
   `NodeMetrics.latency_ms`).

2. **Число копий**
   *k* = quorum + 1 + ⌈log<sub>0.5</sub>(P<sub>target</sub>)⌉,
   где *P<sub>target</sub>* — целевая вероятность успеха (например, 0,999).

3. **Greedy-планирование**
   Пока в `Q` есть задачи:

    1. берём `task`;
    2. сортируем ноды по `score = α·latency + β·util` (α > β для критерия 1);
    3. назначаем первые *k* нод из списка;
    4. если `|running_tasks(node)| > 1` и `|tasks| < |hosts|`, отправляем команду Docker API:

       ```python
       await container.stop(timeout=...); await container.remove()
       ```

4. **Мониторинг & Re-replica**

    * Если в ответе пришёл код ошибки ≥ 500 или превышен `D`, добавляем задачу в `retry_queue` c меткой attempt++.

5. **Завершение** — как только любой репликат прислал «200 OK», остальные копии помечаем «лишними» и можем досрочно
   отменить.

---

## Встраиваем в ваш код

### Collector

Добавьте поле `p_fail` в `NodeMetrics`:

```python
@dataclass
class NodeMetrics:
    ...
    latency_ms: float | None = None
    p_fail: float = 0.01  # скользящее среднее ошибок / запросов
```

Обновляем его в `update_latency()` и при парсинге ответов.

### Планировщик-реплик

Создаём модуль `replicator.py`:

```python
import asyncio, heapq, time
from typing import List
from models import NodeMetrics
from collector import collector_manager


class Replicator:
    def __init__(self, quorum: int, p_target=0.999):
        self.q = asyncio.Queue()
        self.quorum = quorum
        self.p_target = p_target

    def k_copies(self):
        extra = max(0, round(math.log(self.p_target, 0.5)))
        return self.quorum + 1 + extra

    async def submit(self, task):
        await self.q.put(task)

    async def worker(self):
        while True:
            task = await self.q.get()
            metrics = collector_manager.get_metrics()  # свежий снэпшот
            plan = self._greedy(task, metrics)
            await self._dispatch(task, plan)
            self.q.task_done()

    def _greedy(self, task, metrics: List[NodeMetrics]):
        k = self.k_copies()

        # α > β — приоритет на latency
        def score(m): return 0.7 * m.latency_ms + 0.3 * (m.cpu_util + m.mem_util)

        nodes = heapq.nsmallest(k, metrics, key=score)
        return [n.node_id for n in nodes]

    async def _dispatch(self, task, nodes):
        # отправляем асинхронно k копий
        ...
```

В `app.lifespan` поднимаем N корутин-воркеров:

```python
replicator = Replicator(quorum=config.QUORUM)

for _ in range(config.REPL_WORKERS):
    app.state.replica_tasks.append(
        asyncio.create_task(replicator.worker())
    )
```

И из middleware вместо `balancer.choose_node`:

```python
if request.headers.get("X-Replica") == "yes":
    await replicator.submit(request)  # распределённый запуск
    return JSONResponse({"status": "queued"}, 202)
```

### Отключение лишних хостов

В `collector.run_forever` после обновления метрик:

```python
idle = [m for m in self.snapshot.values() if m.running == 0]
tasks = sum(m.running for m in self.snapshot.values())

if tasks < len(self.snapshot) and idle:
    node = min(idle, key=lambda m: m.cpu_util + m.mem_util)
    await docker.containers.get(node.node_id).stop(timeout=20)
```

---

## Проверяем критерии

1. **Время первого ответа** — выбираем ноды по минимальному `latency_ms`;
2. **Суммарное время** — задачи распределяются «жадно», балансируя нагрузку;
3. **Вероятность успеха** — копий ровно `quorum+1+Δ`, где Δ зависит от *p\_target*;
4. **Экономия хостов** — контейнеры без задач останавливаются.

---

## Что ещё стоит доделать

* **p\_fail** вычислять как EWMA ошибок;
* **Дедлайн**: хранить `deadline_at` и отменять реплики по `asyncio.wait_for`;
* **Prometheus**-метрики: процент задач, выполнившихся с первой копии, средний `makespan`;
* **Unit-тест**: эмулировать падающие ноды (контейнер возвращает 5xx, потом `docker stop`).
