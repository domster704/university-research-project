from aiohttp import ClientSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.modules.routing.application.ports.inbound.node.choose_node_port import ChooseNodePort


class ProxyMiddleware(BaseHTTPMiddleware):
    INTERNAL_PATHS = {
        "/stats",
        "/docs",
        "/openapi.json",
        "/redoc"
    }

    def __init__(self, app, choose_node: ChooseNodePort):
        super().__init__(app)
        self.choose_node = choose_node

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self.INTERNAL_PATHS:
            return await call_next(request)

        client: ClientSession = request.app.state.clientSession

        host, port = await self.choose_node.execute()

        async with client.request(
                request.method,
                f"http://{host}:{port}{request.url.path}",
                params=request.query_params,
                headers=dict(request.headers),
                data=await request.body(),
        ) as resp:
            body = await resp.read()

        return Response(
            content=body,
            status_code=resp.status,
            headers=resp.headers,
        )
