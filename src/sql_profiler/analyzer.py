from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional
from .rules import (
    AntiPatternRule,
    CartesianJoinRule,
    DangerousMutationRule,
    IssueSeverity,
    LeadingWildcardRule,
    MissingLimitRule,
    SelectStarRule,
)


@dataclass
class SQLIssue:
    code: str
    title: str
    severity: IssueSeverity
    message: str


@dataclass
class AnalysisResult:
    sql: str
    issues: List[SQLIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def has_danger(self) -> bool:
        return any(i.severity == IssueSeverity.DANGER for i in self.issues)


class SQLAnalyzer:
    """Static SQL anti-pattern detector."""

    def __init__(self, rules: Optional[List[AntiPatternRule]] = None):
        self.rules = rules or [
            SelectStarRule(),
            MissingLimitRule(),
            LeadingWildcardRule(),
            DangerousMutationRule(),
            CartesianJoinRule(),
        ]

    def analyze(self, sql: str) -> AnalysisResult:
        issues = []
        for rule in self.rules:
            msg = rule.check(sql)
            if msg:
                issues.append(
                    SQLIssue(
                        code=rule.code,
                        title=rule.title,
                        severity=rule.severity,
                        message=msg,
                    )
                )
        return AnalysisResult(sql=sql.strip(), issues=issues)
