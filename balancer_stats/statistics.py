import asyncio
import json
from collections import Counter
from typing import Optional, Any

import aiohttp


class AsyncLoadTester:
    def __init__(
            self,
            base_url: str,
            requests_per_load: int = 30,
            delay_between_requests: float = 2.0,
    ):
        self.base_url = base_url.rstrip('/')
        self.requests_per_load = requests_per_load
        self.delay_between_requests = delay_between_requests
        self.session: Optional[aiohttp.ClientSession] = None

        self._results_list: list[str] = []

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def make_request(self, endpoint: str, **kwargs) -> str:
        assert self.session is not None, "Session is not initialized!"
        url = f"{self.base_url}/{endpoint}"
        async with self.session.get(url, **kwargs) as resp:
            json_res = await resp.text()
            print(f"{resp.status} {endpoint}: {json_res}")
            return json_res

    async def load(
            self,
            endpoint: str,
            requests_count: Optional[int] = None,
            delay: Optional[float] = None,
            **request_kwargs,
    ) -> list[Any]:
        """Отправляет requests_count запросов с задержкой delay между ними."""
        tasks = []
        requests_count = requests_count or self.requests_per_load
        delay = delay if delay is not None else self.delay_between_requests

        for i in range(requests_count):
            task = asyncio.create_task(self.make_request(endpoint, **request_kwargs))
            tasks.append(task)
            if i < requests_count - 1:
                await asyncio.sleep(delay)

        res = await asyncio.gather(*tasks)
        self._results_list.extend(res)

        return res

    async def multi_load(self, endpoints: list[str], **kwargs) -> list[list[Any]]:
        """Параллельно запускает несколько load по списку endpoints."""
        tasks = [self.load(endpoint, **kwargs) for endpoint in endpoints]
        return await asyncio.gather(*tasks)

    def stats(self):
        cpu_ports = []
        mem_ports = []
        for line in self._results_list:
            try:
                data = json.loads(line)
                port = str(data.get("port"))
                if "cpu_burn" in data:
                    cpu_ports.append(port)
                elif "mem_burn" in data:
                    mem_ports.append(port)
            except Exception as e:
                print(f"Ошибка разбора строки: {line} ({e})")
        return {
            "cpu": dict(Counter(cpu_ports)),
            "mem": dict(Counter(mem_ports)),
        }


# Пример использования:
async def main():
    async with AsyncLoadTester("http://localhost:8000", requests_per_load=50, delay_between_requests=2) as tester:
        # await tester.multi_load(['cpu', 'mem', 'cpu', 'mem'])

        # Или отдельно:
        # await tester.load('cpu')
        await tester.load('mem')
        print(tester.stats())


if __name__ == '__main__':
    asyncio.run(main())
