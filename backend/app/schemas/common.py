from enum import Enum


class RiskStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class IssueStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ActionStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class EntityType(str, Enum):
    risk = "risk"
    issue = "issue"
