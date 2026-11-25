"""Recherche des établissements parisiens recevant du public (ERP)."""

import re
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.erp_nettoyage import Annuaire, Etablissement, lire_annuaire, normaliser_texte

routes = APIRouter(prefix="/api/erp", tags=["Établissements"])

CHEMIN_FICHIER_ERP = Path(__file__).resolve().parent.parent / "donnees" / "erp-paris.csv"
TAILLE_PAGE_PAR_DEFAUT = 20
TAILLE_PAGE_MAXIMALE = 50
MOTIF_CODE_POSTAL = re.compile(r"^\d{5}$")
MOTIF_TYPE = re.compile(r"^[A-Za-z]{1,3}$")


class PageEtablissements(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(description="Nombre d’établissements correspondant à la recherche", examples=[2])
    page: int = Field(description="Numéro de la page renvoyée (à partir de 1)", examples=[1])
    taille_page: int = Field(description="Nombre maximal de résultats par page", examples=[20])
    lignes_ecartees: int = Field(
        description="Lignes du fichier d’origine inutilisables, donc écartées", examples=[53]
    )
    resultats: list[Etablissement] = Field(description="Établissements de la page demandée")


@lru_cache(maxsize=1)
def charger_annuaire() -> Annuaire:
    """Lit et nettoie le fichier une seule fois."""
    return lire_annuaire(CHEMIN_FICHIER_ERP)


def _refuser(message: str) -> HTTPException:
    return HTTPException(status_code=422, detail=message)


@routes.get(
    "",
    summary="Rechercher des établissements",
    responses={422: {"description": "Paramètre de recherche invalide"}},
)
def rechercher_etablissements(
    annuaire: Annotated[Annuaire, Depends(charger_annuaire)],
    code_postal: str | None = None,
    type_etablissement: str | None = None,
    enseigne: str | None = None,
    page: int = 1,
    taille_page: int = TAILLE_PAGE_PAR_DEFAUT,
) -> PageEtablissements:
    """Filtres facultatifs et combinables : code postal exact (5 chiffres), type d’établissement
    (lettre, principal ou secondaire) et mot contenu dans l’enseigne (sans tenir compte des
    majuscules ni des accents). Les résultats sont paginés."""
    if code_postal is not None and not MOTIF_CODE_POSTAL.match(code_postal):
        raise _refuser("Le code postal doit comporter exactement 5 chiffres.")
    if type_etablissement is not None and not MOTIF_TYPE.match(type_etablissement):
        raise _refuser("Le type d’établissement doit être une lettre, par exemple W ou U.")
    if page < 1:
        raise _refuser("Le numéro de page doit être au moins 1.")
    if not 1 <= taille_page <= TAILLE_PAGE_MAXIMALE:
        raise _refuser(f"La taille de page doit être comprise entre 1 et {TAILLE_PAGE_MAXIMALE}.")

    type_recherche = type_etablissement.upper() if type_etablissement else None
    mot_recherche = normaliser_texte(enseigne) if enseigne else ""
    correspondants = [
        etablissement
        for etablissement, enseigne_normalisee in zip(
            annuaire.etablissements, annuaire.enseignes_normalisees, strict=True
        )
        if (code_postal is None or etablissement.code_postal == code_postal)
        and (
            type_recherche is None
            or type_recherche == etablissement.type_principal
            or type_recherche in etablissement.types_secondaires
        )
        and mot_recherche in enseigne_normalisee
    ]
    debut = (page - 1) * taille_page
    return PageEtablissements(
        total=len(correspondants),
        page=page,
        taille_page=taille_page,
        lignes_ecartees=annuaire.lignes_ecartees,
        resultats=correspondants[debut : debut + taille_page],
    )
