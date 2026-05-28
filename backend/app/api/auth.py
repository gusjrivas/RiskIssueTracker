# TODO: implement auth router
# Endpoints:
#   POST /google    → body: {id_token: str} → TokenResponse
#   POST /register  → body: {email, password, full_name} → TokenResponse (status=pending → 403)
#   POST /login     → body: {email, password} → TokenResponse
from fastapi import APIRouter

router = APIRouter()
