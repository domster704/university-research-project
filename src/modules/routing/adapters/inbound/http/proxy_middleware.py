from aiohttp import ClientSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

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

        try:
            host, port = await self.choose_node.execute()
        except Exception as e:
            return JSONResponse({
                "detail": f"choose node failed: {repr(e)}"
            }, status_code=503)

        target_url = f"http://{host}:{port}{request.url.path}"
        headers = dict(request.headers)

        async with client.request(
                request.method,
                target_url,
                params=request.query_params,
                headers=headers,
                data=await request.body(),
        ) as resp:
            body = await resp.read()

            # Важно: resp.headers в aiohttp — CIMultiDictProxy, Starlette принимает dict/Headers.
            out_headers = dict(resp.headers)

            return Response(
                content=body,
                status_code=resp.status,
                headers=out_headers,
                media_type=out_headers.get("content-type"),
            )
