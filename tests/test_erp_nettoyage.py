from app.erp_nettoyage import nettoyer_csv, normaliser_texte

EN_TETE = (
    "enseigne,numero_de_voie_debut,numero_de_voie_fin,type_et_nom_de_voie,code_postal,ville,"
    "statut_des_locaux,type_principal_ERP,type_secondaire_ERP;\n"
)

EXTRAIT_FICTIF = (
    EN_TETE
    + "    BOULANGERIE   EXEMPLE,2,,PLACE DE L EXEMPLE,75015,Paris,ERP,M,;\n"
    + '"  FONDATION FICTIVE,41,,RUE DU TEST,75013,PARIS,ERP,W,""L,N,O""";\n'
    + "  Crèche LES PETITS EXEMPLES,67,,RUE DU TEST,75018,PARIS,ERP,R,;\n"
    + "Cabinet Dupont, Durand,5,,RUE DU TEST,75008,Paris,ERP,U,\n"
    + "LIGNE TROP COURTE,75001;\n"
    + ";\n"
)


def test_les_espaces_en_trop_et_le_point_virgule_final_sont_retires() -> None:
    annuaire = nettoyer_csv(EXTRAIT_FICTIF)
    premier = annuaire.etablissements[0]
    assert premier.enseigne == "BOULANGERIE EXEMPLE"
    assert premier.voie == "PLACE DE L EXEMPLE"
    assert premier.type_principal == "M"
    assert premier.types_secondaires == []


def test_toutes_les_villes_sont_ecrites_paris() -> None:
    annuaire = nettoyer_csv(EXTRAIT_FICTIF)
    assert {etablissement.ville for etablissement in annuaire.etablissements} == {"Paris"}


def test_les_types_secondaires_multiples_sont_separes() -> None:
    annuaire = nettoyer_csv(EXTRAIT_FICTIF)
    fondation = annuaire.etablissements[1]
    assert fondation.enseigne == "FONDATION FICTIVE"
    assert fondation.types_secondaires == ["L", "N", "O"]


def test_une_enseigne_contenant_une_virgule_est_reparee() -> None:
    annuaire = nettoyer_csv(EXTRAIT_FICTIF)
    cabinet = annuaire.etablissements[3]
    assert cabinet.enseigne == "Cabinet Dupont, Durand"
    assert cabinet.numero_debut == "5"
    assert cabinet.code_postal == "75008"


def test_une_ligne_irreparable_est_ecartee_et_comptee() -> None:
    annuaire = nettoyer_csv(EXTRAIT_FICTIF)
    assert len(annuaire.etablissements) == 4
    assert annuaire.lignes_ecartees == 1
    assert all("TROP COURTE" not in etablissement.enseigne for etablissement in annuaire.etablissements)


def test_normaliser_texte_ignore_accents_et_majuscules() -> None:
    assert normaliser_texte("  Crèche   LES Ptits ") == "creche les ptits"
