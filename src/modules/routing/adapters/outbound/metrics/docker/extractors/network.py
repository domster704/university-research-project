from src.modules.routing.domain.policies.metric_extractor import MetricExtractor


class NetworkExtractor(MetricExtractor):
    def extract(self, raw_stats: dict) -> dict[str, float]:
        net = raw_stats.get("networks", {})
        net_in = sum(v.get("rx_bytes", 0) for v in net.values())
        net_out = sum(v.get("tx_bytes", 0) for v in net.values())
        return {
            "net_in_bytes": int(net_in),
            "net_out_bytes": int(net_out),
        }
