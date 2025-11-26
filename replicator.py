import asyncio
import hashlib
import json
import time
from aiohttp import ClientSession
from typing import List, Dict

from collector import collector_manager
from models import NodeMetrics


class Replicator:

    def __init__(self):
        self.session: ClientSession | None = None

    async def setup(self):
        self.session = ClientSession()

    async def shutdown(self):
        if self.session:
            await self.session.close()

    # -------- эвристики выбора нод -------- #

    def _choose_nodes_deterministic(self, metrics: List[NodeMetrics], k: int):
        def score(m):
            return 0.7 * (m.latency_ms or 1e6) + 0.2 * m.cpu_util + 0.1 * m.mem_util

        return sorted(metrics, key=score)[:k]

    def _choose_nodes_stochastic(self, metrics: List[NodeMetrics], k: int):
        metrics_sorted = sorted(metrics, key=lambda m: m.latency_ms or 1e6)
        half = k // 2

        best_half = metrics_sorted[:half]
        import random
        rest = metrics_sorted[half:]
        random_half = random.sample(rest, k - half) if len(rest) >= (k - half) else rest

        return best_half + random_half

    # -------- валидация -------- #

    @staticmethod
    def _hash(body: bytes):
        return hashlib.sha256(body).hexdigest()

    def _validate_first_success(self, results: List):
        for status, body in results:
            if 200 <= status < 300:
                return status, body
        return results[0]

    def _validate_majority(self, results: List):
        counter = {}
        for status, body in results:
            if 200 <= status < 300:
                counter.setdefault(body, 0)
                counter[body] += 1
        best = max(counter.items(), key=lambda kv: kv[1])[0]
        for st, body in results:
            if body == best:
                return st, body

    def _validate_hash(self, results: List):
        hashes = {self._hash(body): (status, body) for status, body in results}
        if len(hashes) == 1:
            return next(iter(hashes.values()))
        return next(iter(hashes.values()))  # fallback

    # -------- выполнение репликаций -------- #

    async def execute(self,
                      request,
                      rep_count: int,
                      heuristic: str,
                      validator: str,
                      deadline_ms: int) -> (int, bytes):

        metrics, _ = collector_manager.get_metrics()

        # -------- выбор нод --------
        if heuristic == "stochastic":
            selected = self._choose_nodes_stochastic(metrics, rep_count)
        elif heuristic == "deterministic":
            selected = self._choose_nodes_deterministic(metrics, rep_count)
        else:
            selected = self._choose_nodes_deterministic(metrics, rep_count)

        # -------- отправляем параллельные запросы -------- #

        async def do_req(node: NodeMetrics):
            host, port = config.NODE_ENDPOINTS[node.node_id]
            url = f"http://{host}:{port}{request.url.path}"
            async with self.session.request(
                    method=request.method,
                    url=url,
                    headers=request.headers,
                    data=await request.body()
            ) as resp:
                return resp.status, await resp.read()

        tasks = [asyncio.create_task(do_req(m)) for m in selected]

        done, pending = await asyncio.wait(
            tasks,
            timeout=deadline_ms / 1000,
            return_when=asyncio.ALL_COMPLETED
        )

        results = [t.result() for t in done]

        for p in pending:
            p.cancel()

        # -------- валидация -------- #
        if validator == "first-success":
            return self._validate_first_success(results)
        if validator == "majority":
            return self._validate_majority(results)
        if validator == "hash":
            return self._validate_hash(results)

        return self._validate_first_success(results)


"""
replicator = Replicator()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await replicator.setup()
    ...
    yield
    await replicator.shutdown()


@app.middleware("http")
async def proxy(request: Request, call_next):
    # читаем заголовки BRS
    rep_count_header = request.headers.get("X-Replications-Count")
    rep_all = request.headers.get("X-Replications-All") == "True"
    heuristic = request.headers.get("X-Replications-Heuristic", "deterministic")
    validator = request.headers.get("X-Replications-Validator", "first-success")
    deadline = int(request.headers.get("X-Balancer-Deadline", 3000))

    if rep_count_header or rep_all:
        if rep_all:
            metrics, _ = collector_manager.get_metrics()
            rep_count = len(metrics)
        else:
            rep_count = 3 if rep_count_header == "True" else int(rep_count_header)

        status, body = await replicator.execute(
            request,
            rep_count=rep_count,
            heuristic=heuristic,
            validator=validator,
            deadline_ms=deadline
        )
        return Response(content=body, status_code=status)

    # обычный балансировщик без репликаций
    ...

"""
