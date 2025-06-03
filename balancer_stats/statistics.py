import asyncio
import random

import aiohttp


class Session:
    session: aiohttp.ClientSession | None = None


async def make_request(config: str, n: int) -> str:
    """
    Один HTTP-запрос; session передаём снаружи, чтобы соединения переиспользовались.
    """
    # await asyncio.sleep(random.randint(0, 200) / 100)
    async with Session.session.get(f"http://localhost:8000/{config}") as resp:
        text = await resp.text()
        print(resp.status, text)
        return text


async def load(config: str, n: int = 30):
    """
    Отправляет n запросов параллельно на /cpu или /mem.
    """
    tasks = [make_request(config, n) for _ in range(n)]
    await asyncio.gather(*tasks)


async def main():
    Session.session = aiohttp.ClientSession()
    await asyncio.gather(
        load('cpu'),
        load('cpu'),
        load('cpu'),
        # load('mem'),
        # load('mem'),
        # load('mem'),
    )
    await Session.session.close()


if __name__ == '__main__':
    asyncio.run(main())
