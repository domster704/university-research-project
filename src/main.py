from fastapi import FastAPI

from src.adapters.inbound.http.fastapi_proxy import router, set_port
from src.bootstrap.container import build_choose_node_port


def create_app() -> FastAPI:
    app = FastAPI()
    choose_node_port = build_choose_node_port()
    set_port(choose_node_port)
    app.include_router(router)
    return app


app = create_app()
