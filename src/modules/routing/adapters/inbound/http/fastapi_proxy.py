from fastapi import APIRouter, Request

from src.modules.routing.application.dto.incoming_request import IncomingRequest
from src.modules.routing.application.ports.inbound.node.choose_node_port import ChooseNodePort


class ChooseNodeRouter:
    def __init__(self, choose_node: ChooseNodePort):
        self.router = APIRouter()

        @self.router.get("/choose")
        async def choose():
            return await choose_node.execute()

        @self.router.api_route("/{path:path}", methods=["GET", "POST"])
        async def proxy(request: Request):
            host, port = await choose_node.execute()
            return {"host": host, "port": port}
