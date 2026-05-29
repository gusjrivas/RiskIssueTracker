from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.issue import Issue  # noqa: F401 — must precede Risk (FK circular)
from app.models.risk import Risk  # noqa: F401
