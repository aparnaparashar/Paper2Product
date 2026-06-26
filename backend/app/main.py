from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import create_tables
from app.routers import auth, projects

settings = get_settings()

app = FastAPI(
    title="Research-to-Product Advisor",
    version="2.0.0",
    description="15-agent pipeline with debate, scoring, and full traceability",
)

# Auth uses Bearer tokens (not cookies), so allow_credentials=False lets us
# safely use allow_origins=["*"]. Combining "*" with credentials=True is
# invalid per the CORS spec — browsers then drop the ACAO header entirely,
# which is what causes "No 'Access-Control-Allow-Origin' header" errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)


@app.on_event("startup")
def startup():
    create_tables()  # auto-creates all tables on first run (no Alembic needed)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}