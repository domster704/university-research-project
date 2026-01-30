import asyncio


class ReplicateRequestUseCase:
    def __init__(
            self,
            metrics_provider,
            registry,
            http_client,
            balancer,
            replicas: int,
    ):
        self.metrics_provider = metrics_provider
        self.registry = registry
        self.http_client = http_client
        self.balancer = balancer
        self.replicas = replicas

    async def execute(self, request):
        metrics = await self.metrics_provider.get_current()
        ranked = self.balancer.rank(metrics)[:self.replicas]

        tasks = [
            self.http_client.send(
                *self.registry.get_endpoint(node.node_id),
                request,
            )
            for node in ranked
        ]

        done, _ = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED,
        )

        return list(done)[0].result()
