import enum
import re
from typing import Dict, List, Optional


class IssueSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    DANGER = "DANGER"


class AntiPatternRule:
    def __init__(self, code: str, title: str, severity: IssueSeverity, description: str):
        self.code = code
        self.title = title
        self.severity = severity
        self.description = description

    def check(self, sql: str) -> Optional[str]:
        raise NotImplementedError


class SelectStarRule(AntiPatternRule):
    def __init__(self):
        super().__init__(
            code="PERF001",
            title="SELECT * Usage",
            severity=IssueSeverity.WARNING,
            description="Using 'SELECT *' fetches unnecessary columns, slows serialization, and prevents covering indexes.",
        )

    def check(self, sql: str) -> Optional[str]:
        cleaned = re.sub(r"\s+", " ", sql.strip())
        if re.search(r"\bSELECT\s+(DISTINCT\s+)?(\w+\.)?\*\s+FROM\b", cleaned, re.IGNORECASE):
            return "Avoid 'SELECT *'; specify only the needed columns."
        return None


class MissingLimitRule(AntiPatternRule):
    def __init__(self):
        super().__init__(
            code="PERF002",
            title="Unbounded SELECT Query",
            severity=IssueSeverity.WARNING,
            description="SELECT query on tables without a LIMIT clause can load millions of rows into memory.",
        )

    def check(self, sql: str) -> Optional[str]:
        cleaned = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
        cleaned = re.sub(r"--[^\n]*", "", cleaned).strip().upper()
        if cleaned.startswith("SELECT") and "COUNT(" not in cleaned and "LIMIT" not in cleaned and "TOP " not in cleaned and "FETCH FIRST" not in cleaned:
            return "Query has no LIMIT clause. Large result sets may exhaust server memory."
        return None


class LeadingWildcardRule(AntiPatternRule):
    def __init__(self):
        super().__init__(
            code="PERF003",
            title="Leading Wildcard in LIKE",
            severity=IssueSeverity.WARNING,
            description="LIKE '%text' prevents B-Tree index lookups and causes full table scans.",
        )

    def check(self, sql: str) -> Optional[str]:
        if re.search(r"\bLIKE\s+['\"]%[a-zA-Z0-9]", sql, re.IGNORECASE):
            return "Leading wildcard '%...' disables B-tree index lookup and triggers full table scan."
        return None


class DangerousMutationRule(AntiPatternRule):
    def __init__(self):
        super().__init__(
            code="DANG001",
            title="Unconstrained UPDATE or DELETE",
            severity=IssueSeverity.DANGER,
            description="UPDATE or DELETE without a WHERE clause will modify or wipe the entire table.",
        )

    def check(self, sql: str) -> Optional[str]:
        cleaned = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
        cleaned = re.sub(r"--[^\n]*", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip().upper()
        if (cleaned.startswith("UPDATE ") or cleaned.startswith("DELETE ")) and " WHERE " not in cleaned:
            return "Catastrophic query: Missing WHERE clause will update/delete all rows in the table."
        return None


class CartesianJoinRule(AntiPatternRule):
    def __init__(self):
        super().__init__(
            code="PERF004",
            title="Implicit Cartesian Join",
            severity=IssueSeverity.DANGER,
            description="Listing multiple tables in FROM without explicit JOIN ON causes cross-product multiplication.",
        )

    def check(self, sql: str) -> Optional[str]:
        m = re.search(r"\bFROM\s+([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)", sql, re.IGNORECASE)
        if m:
            return f"Implicit Cartesian join between '{m.group(1)}' and '{m.group(2)}'. Use explicit INNER JOIN with ON."
        return None
