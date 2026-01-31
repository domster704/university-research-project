from src.modules.routing.domain.strategies.metric_extractor import MetricExtractor


class MemoryExtractor(MetricExtractor):
    def extract(self, raw_stats: dict) -> dict[str, float]:
        mem = raw_stats["memory_stats"]
        mem_util = mem["usage"] / (mem["limit"] + 1e-12)
        return {"mem_util": float(mem_util)}
