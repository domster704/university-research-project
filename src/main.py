import uvicorn
from fastapi import FastAPI

from src.modules.routing.adapters.inbound.http.proxy_middleware import ProxyMiddleware
from src.modules.routing.adapters.inbound.http.router import ChooseNodeRouter
from src.modules.routing.bootstrap.container import RoutingModule
from src.modules.routing.bootstrap.lifespan import lifespan


def create_app() -> FastAPI:
    module = RoutingModule()

    app = FastAPI(lifespan=lambda app_: lifespan(app_, module))

    app.include_router(ChooseNodeRouter(module.choose_node_uc).router)

    app.add_middleware(ProxyMiddleware, choose_node=module.choose_node_uc)

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(
        app,
        port=8000,
        loop="asyncio",
        factory=False,
    )
