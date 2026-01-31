from fastapi import FastAPI

from src.modules.routing.adapters.inbound.http.fastapi_proxy import ChooseNodeRouter
from src.modules.routing.application.usecase import ChooseNodeUseCase
from src.modules.routing.bootstrap.container import build_choose_node_port


def create_app() -> FastAPI:
    app = FastAPI()
    choose_node_port: ChooseNodeUseCase = build_choose_node_port()
    router = ChooseNodeRouter(choose_node_port).router
    app.include_router(router)
    return app


app = create_app()
