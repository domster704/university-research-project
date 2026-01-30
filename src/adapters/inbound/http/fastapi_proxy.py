from fastapi import APIRouter, Request

from src.application.dto.incoming_request import IncomingRequest

router = APIRouter()
_choose_node_port = None


def set_port(port):
    global _choose_node_port
    _choose_node_port = port


@router.api_route("/{path:path}", methods=["GET", "POST"])
async def proxy(request: Request):
    host, port = await _choose_node_port.execute()
    return {"host": host, "port": port}
