import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class QueryMetrics:
    intent: str = ""
    intent_label: str = ""
    search_time_ms: float = 0.0
    llm_time_ms: float = 0.0
    chunk_count: int = 0
    avg_score: float = 0.0
    confidence: float = 0.0
    tokens_sent: int = 0
    tokens_received: int = 0
    depth: str = ""
    style: str = ""
    start_time: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "intent": self.intent,
            "intent_label": self.intent_label,
            "search_time_ms": round(self.search_time_ms, 2),
            "llm_time_ms": round(self.llm_time_ms, 2),
            "total_time_ms": round((time.time() - self.start_time) * 1000, 2),
            "chunk_count": self.chunk_count,
            "avg_score": round(self.avg_score, 4),
            "confidence": round(self.confidence, 2),
            "tokens_sent": self.tokens_sent,
            "tokens_received": self.tokens_received,
            "depth": self.depth,
            "style": self.style,
        }


_metrics_history: list[QueryMetrics] = []
MAX_METRICS = 100


def register_metrics(metrics: QueryMetrics) -> None:
    _metrics_history.append(metrics)
    if len(_metrics_history) > MAX_METRICS:
        _metrics_history.pop(0)


def get_metrics_history() -> list[dict]:
    return [m.to_dict() for m in _metrics_history]
