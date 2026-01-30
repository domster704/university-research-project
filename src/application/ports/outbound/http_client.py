from typing import Protocol

from src.application.dto.http_response import HttpResponse
from src.application.dto.incoming_request import IncomingRequest


class HttpClient(Protocol):
    async def send(
            self,
            host: str,
            port: int,
            request: IncomingRequest,
    ) -> HttpResponse:
        ...
