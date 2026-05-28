import math
from enum import Enum
from typing import Generic, List, TypeVar

from pydantic import BaseModel


class RiskStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"
    derived = "derived"


class IssueStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class ProbabilityLevel(str, Enum):
    muy_baja = "muy_baja"
    baja = "baja"
    media = "media"
    alta = "alta"
    muy_alta = "muy_alta"


class ImpactLevel(str, Enum):
    muy_bajo = "muy_bajo"
    bajo = "bajo"
    medio = "medio"
    alto = "alto"
    muy_alto = "muy_alto"


class Proximity(str, Enum):
    corto_plazo = "corto_plazo"
    mediano_plazo = "mediano_plazo"
    largo_plazo = "largo_plazo"


class ExposureZone(str, Enum):
    bajo = "bajo"
    medio = "medio"
    alto = "alto"


class RiskCategory(str, Enum):
    calendario = "calendario"
    alcance = "alcance"
    ingresos = "ingresos"
    costos = "costos"
    presupuesto = "presupuesto"
    equipo = "equipo"
    gestion = "gestion"


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class UserStatus(str, Enum):
    pending = "pending"
    active = "active"
    inactive = "inactive"


class EntityType(str, Enum):
    risk = "risk"
    issue = "issue"
    project = "project"
    user = "user"


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def build(cls, items: List[T], total: int, page: int, size: int) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size > 0 else 0,
        )
