from contextlib import asynccontextmanager

import aiohttp
import uvicorn
from fastapi import FastAPI

from src.modules.routing.adapters.inbound.http.proxy_middleware import ProxyMiddleware
from src.modules.routing.adapters.inbound.http.router import ChooseNodeRouter
from src.modules.routing.application.usecase.choose_node import ChooseNodeUseCase
from src.modules.routing.bootstrap.container import build_choose_node_port


@asynccontextmanager
async def lifespan(app: FastAPI):
    session = aiohttp.ClientSession(...)
    app.state.clientSession = session
    yield
    await session.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    choose_node_port: ChooseNodeUseCase = build_choose_node_port()
    router = ChooseNodeRouter(choose_node_port).router

    app.include_router(router)
    app.middleware(ProxyMiddleware)

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(
        app,
        port=8000,
        loop="asyncio",
        factory=False,
    )
