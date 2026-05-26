from app.schemas.common import Severity


def _normalize_to_5(value: int, max_value: int) -> float:
    return 1 + (value - 1) * (4 / (max_value - 1))


def get_severity_score(probability: int, impact: int, urgency: int, scope: int) -> float:
    urgency_norm = _normalize_to_5(urgency, 3)
    scope_norm = _normalize_to_5(scope, 3)
    score = (
        probability * 0.35
        + impact * 0.35
        + urgency_norm * 0.15
        + scope_norm * 0.15
    ) / 5
    return round(score, 4)


def score_to_severity(score: float) -> Severity:
    if score < 0.40:
        return Severity.low
    if score < 0.60:
        return Severity.medium
    if score < 0.80:
        return Severity.high
    return Severity.critical


def calculate_severity(probability: int, impact: int, urgency: int, scope: int) -> Severity:
    score = get_severity_score(probability, impact, urgency, scope)
    return score_to_severity(score)
