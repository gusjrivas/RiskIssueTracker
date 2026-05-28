# TODO: implement admin router (requiere role=admin en todos los endpoints)
# Endpoints:
#   GET    /users               → PaginatedResponse[UserResponse]
#   PATCH  /users/{id}/approve      → UserResponse
#   PATCH  /users/{id}/deactivate   → UserResponse
from fastapi import APIRouter

router = APIRouter()
