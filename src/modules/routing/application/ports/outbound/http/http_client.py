from typing import Protocol

from src.modules.routing.application.dto.http_response import HttpResponse
from src.modules.routing.application.dto.incoming_request import IncomingRequest


class HttpClient(Protocol):
    async def send(
        self,
        host: str,
        port: int,
        request: IncomingRequest,
    ) -> HttpResponse: ...
