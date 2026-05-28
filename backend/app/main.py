from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import risks, issues, projects, history, auth, admin

app = FastAPI(title="RiskIssueTracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
app.include_router(admin.router, prefix=f"{settings.api_prefix}/admin", tags=["admin"])
app.include_router(projects.router, prefix=f"{settings.api_prefix}/projects", tags=["projects"])
app.include_router(risks.router, prefix=f"{settings.api_prefix}/risks", tags=["risks"])
app.include_router(issues.router, prefix=f"{settings.api_prefix}/issues", tags=["issues"])
app.include_router(history.router, prefix=f"{settings.api_prefix}/history", tags=["history"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
