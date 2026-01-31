from typing import Protocol


class ChooseNodePort(Protocol):
    async def execute(self) -> tuple[str, int]:
        ...
