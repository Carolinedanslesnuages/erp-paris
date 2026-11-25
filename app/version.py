"""Contrat repo-version-json (format Dockerflow) : le fichier de l'image, sinon « dev »."""

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.config import reglages

routes = APIRouter()

VERSION_DEV: dict[str, Any] = {
    "source": "",
    "version": "dev",
    "commit": "",
    "build": "",
    "code_date": "",
    "changes": [],
    "history": [],
}


def lire_version(fichier: str | None = None) -> dict[str, Any]:
    try:
        contenu: dict[str, Any] = json.loads(
            Path(fichier or reglages.version_json).read_text(encoding="utf-8")
        )
        return contenu
    except (OSError, ValueError):
        return dict(VERSION_DEV)


@routes.get("/__version__", include_in_schema=False)
@routes.get("/api/__version__", include_in_schema=False)
def version() -> JSONResponse:
    return JSONResponse(lire_version(), headers={"Cache-Control": "no-store"})
