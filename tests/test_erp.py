from fastapi.testclient import TestClient

from app.erp import charger_annuaire
from app.erp_nettoyage import Annuaire, nettoyer_csv
from app.main import app
from tests.test_erp_nettoyage import EXTRAIT_FICTIF

client = TestClient(app)


def _utiliser_annuaire(annuaire: Annuaire) -> None:
    app.dependency_overrides[charger_annuaire] = lambda: annuaire


def setup_function() -> None:
    _utiliser_annuaire(nettoyer_csv(EXTRAIT_FICTIF))


def teardown_function() -> None:
    app.dependency_overrides.clear()


def _enseignes(reponse_json: dict[str, object]) -> list[str]:
    resultats = reponse_json["resultats"]
    assert isinstance(resultats, list)
    return [resultat["enseigne"] for resultat in resultats]


def test_recherche_par_code_postal_exact() -> None:
    reponse = client.get("/api/erp", params={"code_postal": "75013"})
    assert reponse.status_code == 200
    assert _enseignes(reponse.json()) == ["FONDATION FICTIVE"]
    assert reponse.json()["total"] == 1


def test_recherche_par_type_principal_et_secondaire() -> None:
    principal = client.get("/api/erp", params={"type_etablissement": "w"}).json()
    assert _enseignes(principal) == ["FONDATION FICTIVE"]
    secondaire = client.get("/api/erp", params={"type_etablissement": "N"}).json()
    assert _enseignes(secondaire) == ["FONDATION FICTIVE"]


def test_recherche_par_enseigne_sans_accent_ni_majuscule() -> None:
    reponse = client.get("/api/erp", params={"enseigne": "creche"})
    assert _enseignes(reponse.json()) == ["Crèche LES PETITS EXEMPLES"]


def test_les_filtres_se_combinent() -> None:
    reponse = client.get(
        "/api/erp", params={"code_postal": "75018", "enseigne": "petits", "type_etablissement": "R"}
    )
    assert reponse.json()["total"] == 1
    aucun = client.get("/api/erp", params={"code_postal": "75013", "enseigne": "petits"})
    assert aucun.json()["total"] == 0


def test_resultats_pagines() -> None:
    premiere = client.get("/api/erp", params={"taille_page": 3}).json()
    assert premiere["total"] == 4
    assert len(premiere["resultats"]) == 3
    suivante = client.get("/api/erp", params={"taille_page": 3, "page": 2}).json()
    assert _enseignes(suivante) == ["Cabinet Dupont, Durand"]


def test_la_reponse_indique_les_lignes_ecartees() -> None:
    assert client.get("/api/erp").json()["lignes_ecartees"] == 1


def test_recherche_sans_resultat_renvoie_une_liste_vide() -> None:
    reponse = client.get("/api/erp", params={"enseigne": "introuvable"})
    assert reponse.status_code == 200
    assert reponse.json()["resultats"] == []
    assert reponse.json()["total"] == 0


def test_code_postal_invalide_renvoie_un_message_clair() -> None:
    reponse = client.get("/api/erp", params={"code_postal": "75A"})
    assert reponse.status_code == 422
    assert reponse.json()["detail"] == "Le code postal doit comporter exactement 5 chiffres."


def test_parametres_de_page_invalides() -> None:
    assert client.get("/api/erp", params={"page": 0}).status_code == 422
    assert client.get("/api/erp", params={"taille_page": 51}).status_code == 422
    assert client.get("/api/erp", params={"type_etablissement": "123"}).status_code == 422


def test_les_routes_figurent_dans_la_documentation() -> None:
    openapi = client.get("/api/openapi.json").json()
    operation = openapi["paths"]["/api/erp"]["get"]
    assert operation["summary"] == "Rechercher des établissements"
    assert "422" in operation["responses"]


def test_le_vrai_fichier_est_lisible() -> None:
    app.dependency_overrides.clear()
    reponse = client.get("/api/erp", params={"code_postal": "75015", "taille_page": 5})
    assert reponse.status_code == 200
    assert reponse.json()["total"] > 0
