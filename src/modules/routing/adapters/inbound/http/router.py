from fastapi import APIRouter, Request

from src.modules.routing.application.ports.inbound.node.choose_node_port import ChooseNodePort


class ChooseNodeRouter:
    def __init__(self, choose_node: ChooseNodePort):
        self.router = APIRouter()

        @self.router.get("/choose")
        async def choose():
            host, port = await choose_node.execute()
            return {"host": host, "port": port}

        # @self.router.get("/stats")
        # async def stats():
        #     """Сводные метрики по задержкам и ресурсам."""
        #     data = get_avg_resources()
        #     return JSONResponse(data)
