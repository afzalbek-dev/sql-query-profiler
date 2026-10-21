from collections import defaultdict
from dataclasses import dataclass, field
import re
import time
from typing import Any, Dict, List, Optional
from .analyzer import AnalysisResult, SQLAnalyzer


def _normalize_sql(sql: str) -> str:
    """Normalize SQL by replacing literals with placeholders to identify repeated patterns."""
    s = re.sub(r"'[^']*'", "?", sql)
    s = re.sub(r"\b\d+\b", "?", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s.upper()


@dataclass
class QueryRecord:
    raw_sql: str
    duration_ms: float
    analysis: AnalysisResult
    timestamp: float = field(default_factory=time.time)


class SQLProfiler:
    """Session-level SQL query profiler with automatic N+1 problem detection."""

    def __init__(self, analyzer: Optional[SQLAnalyzer] = None, n_plus_one_threshold: int = 3):
        self.analyzer = analyzer or SQLAnalyzer()
        self.n_plus_one_threshold = n_plus_one_threshold
        self.records: List[QueryRecord] = []

    def record_query(self, sql: str, duration_ms: float = 0.0) -> QueryRecord:
        analysis = self.analyzer.analyze(sql)
        rec = QueryRecord(raw_sql=sql.strip(), duration_ms=duration_ms, analysis=analysis)
        self.records.append(rec)
        return rec

    def detect_n_plus_one(self) -> Dict[str, int]:
        """Detect repeated query patterns exceeding the threshold."""
        patterns: Dict[str, int] = defaultdict(int)
        for r in self.records:
            norm = _normalize_sql(r.raw_sql)
            patterns[norm] += 1

        return {k: count for k, count in patterns.items() if count >= self.n_plus_one_threshold}

    def generate_report(self) -> Dict[str, Any]:
        total_queries = len(self.records)
        total_duration = sum(r.duration_ms for r in self.records)
        all_issues = sum(len(r.analysis.issues) for r in self.records)
        n1_patterns = self.detect_n_plus_one()

        return {
            "total_queries": total_queries,
            "total_duration_ms": round(total_duration, 2),
            "total_issues": all_issues,
            "n_plus_one_detected": len(n1_patterns) > 0,
            "n_plus_one_patterns": n1_patterns,
        }

    def __enter__(self):
        self.records.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
