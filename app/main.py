"""L'application FastAPI : un module de routes par domaine (`app/<domaine>.py`), branché ici."""

from fastapi import FastAPI

from app import sante, version

app = FastAPI(
    title="ERP Paris",
    description="Documentation de l’API (OpenAPI), générée à partir du code. Données fictives uniquement.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)
app.include_router(sante.routes)
app.include_router(version.routes)
