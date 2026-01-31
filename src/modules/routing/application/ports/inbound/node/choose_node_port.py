from typing import Protocol


class ChooseNodePort(Protocol):
    async def execute(self) -> tuple[str, str, int]:
        """
        Returns:
            (node_id, host, port)
        """
        ...
