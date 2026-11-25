"""Lecture et nettoyage du fichier CSV brut des établissements parisiens recevant du public."""

import csv
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

MOTIF_CODE_POSTAL = re.compile(r"^\d{5}$")
POSITION_MINIMALE_CODE_POSTAL = 4  # enseigne, numéro de début, numéro de fin, voie
NOMBRE_MINIMAL_CHAMPS_APRES_CODE_POSTAL = 3  # ville, statut, type principal


class Etablissement(BaseModel):
    """Un établissement recevant du public, une fois nettoyé."""

    model_config = ConfigDict(extra="forbid")

    enseigne: str = Field(description="Nom de l’établissement", examples=["Boulangerie Exemple"])
    numero_debut: str = Field(description="Numéro de voie (début), vide si inconnu", examples=["12"])
    numero_fin: str = Field(description="Numéro de voie (fin), vide si inconnu", examples=["14"])
    voie: str = Field(description="Type et nom de la voie", examples=["RUE DE L’EXEMPLE"])
    code_postal: str = Field(description="Code postal à 5 chiffres", examples=["75011"])
    ville: str = Field(description="Ville, toujours écrite « Paris »", examples=["Paris"])
    statut: str = Field(description="Statut des locaux", examples=["ERP"])
    type_principal: str = Field(description="Lettre du type principal d’établissement", examples=["M"])
    types_secondaires: list[str] = Field(
        description="Lettres des types secondaires, une par élément", examples=[["N", "L"]]
    )


@dataclass
class Annuaire:
    """Établissements propres, avec leur clé de recherche, et nombre de lignes écartées."""

    etablissements: list[Etablissement] = field(default_factory=list)
    enseignes_normalisees: list[str] = field(default_factory=list)
    lignes_ecartees: int = 0


def normaliser_texte(texte: str) -> str:
    """Minuscules, sans accents, espaces uniques : sert à comparer et à rechercher."""
    sans_accents = "".join(
        caractere
        for caractere in unicodedata.normalize("NFKD", texte)
        if not unicodedata.combining(caractere)
    )
    return " ".join(sans_accents.casefold().split())


def _espaces_uniques(texte: str) -> str:
    return " ".join(texte.split())


def _champs_de_la_ligne(ligne: str) -> list[str]:
    """Retire le point-virgule final et les guillemets qui enveloppent parfois toute la ligne."""
    ligne = ligne.strip()
    ligne = ligne.removesuffix(";")
    if len(ligne) >= 2 and ligne.startswith('"') and ligne.endswith('"'):
        ligne = ligne[1:-1].replace('""', '"')
    return next(csv.reader([ligne]))


def _nettoyer_ligne(ligne: str) -> Etablissement | None:
    """Renvoie l'établissement propre, ou None si la ligne est trop abîmée pour être réparée.

    Le code postal sert de repère : ce qui le précède est l'enseigne (qui peut contenir des
    virgules), les deux numéros et la voie ; ce qui le suit est la ville, le statut et les types.
    """
    champs = _champs_de_la_ligne(ligne)
    positions_code_postal = [
        position
        for position, valeur in enumerate(champs)
        if position >= POSITION_MINIMALE_CODE_POSTAL and MOTIF_CODE_POSTAL.match(valeur.strip())
    ]
    if not positions_code_postal:
        return None
    position = positions_code_postal[-1]
    apres = champs[position + 1 :]
    if len(apres) < NOMBRE_MINIMAL_CHAMPS_APRES_CODE_POSTAL:
        return None
    enseigne = _espaces_uniques(",".join(champs[: position - 3]))
    type_principal = apres[2].strip().upper()
    if not enseigne or not type_principal:
        return None
    types_secondaires = [
        type_secondaire.strip().upper()
        for type_secondaire in ",".join(apres[3:]).split(",")
        if type_secondaire.strip()
    ]
    return Etablissement(
        enseigne=enseigne,
        numero_debut=_espaces_uniques(champs[position - 3]),
        numero_fin=_espaces_uniques(champs[position - 2]),
        voie=_espaces_uniques(champs[position - 1]),
        code_postal=champs[position].strip(),
        ville="Paris",
        statut=_espaces_uniques(apres[1]),
        type_principal=type_principal,
        types_secondaires=types_secondaires,
    )


def nettoyer_csv(contenu: str) -> Annuaire:
    """Nettoie tout le contenu du fichier : la première ligne (en-têtes) est ignorée.

    Les lignes vides (que des séparateurs) ne sont pas des données : elles ne sont pas comptées.
    """
    annuaire = Annuaire()
    for ligne in contenu.splitlines()[1:]:
        if not ligne.strip(' ;,"'):
            continue
        etablissement = _nettoyer_ligne(ligne)
        if etablissement is None:
            annuaire.lignes_ecartees += 1
            continue
        annuaire.etablissements.append(etablissement)
        annuaire.enseignes_normalisees.append(normaliser_texte(etablissement.enseigne))
    return annuaire


def lire_annuaire(chemin: Path) -> Annuaire:
    return nettoyer_csv(chemin.read_text(encoding="utf-8-sig"))
