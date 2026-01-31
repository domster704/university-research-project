from src.modules.routing.domain.strategies.metric_extractor import MetricExtractor


class LatencyExtractor(MetricExtractor):
    def extract(self, raw_stats: dict) -> dict[str, float]:
        # docker stats latency не дают напрямую
        # можно обновлять отдельно из proxy
        return {}
