"""Santé de l'API et racine du service."""

from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

routes = APIRouter()


class EtatApi(BaseModel):
    statut: str = Field(examples=["ok"], description="L’API répond")


@routes.get("/", include_in_schema=False)
def racine() -> RedirectResponse:
    """La racine mène à la documentation (c'est elle que montre l'aperçu d'ADA)."""
    return RedirectResponse("/api/docs", status_code=302)


@routes.get("/api", tags=["Santé"], summary="L’API est prête")
def etat() -> EtatApi:
    return EtatApi(statut="ok")
