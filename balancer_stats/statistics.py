import asyncio

import aiohttp

async def make_request() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8000/cpu") as resp:
            print(resp.status, await resp.text())
            return await resp.text()

async def main():
    res = []
    tasks = []
    for i in range(100):
        res_ = await make_request()
        res.append(res_)
    print(res)

if __name__ == '__main__':
    asyncio.run(main())