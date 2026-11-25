from app.config import Reglages


def test_adresse_de_la_base_avec_le_pilote_psycopg() -> None:
    reglages = Reglages(database_url="postgresql://utilisateur:secret@db:5432/base")
    assert reglages.adresse_base == "postgresql+psycopg://utilisateur:secret@db:5432/base"


def test_l_option_schema_de_prisma_est_retiree_les_autres_gardees() -> None:
    reglages = Reglages(database_url="postgresql://a:b@db:5432/base?schema=public&sslmode=require")
    assert reglages.adresse_base == "postgresql+psycopg://a:b@db:5432/base?sslmode=require"
