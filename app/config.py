"""Configuration lue dans l'environnement (fichier .env en local, jamais commité)."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic_settings import BaseSettings, SettingsConfigDict


class Reglages(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://erp-paris:erp-paris@localhost:5432/erp-paris"
    version_json: str = "/app/version.json"

    @property
    def adresse_base(self) -> str:
        """Adresse SQLAlchemy : pilote psycopg 3 explicite, sans l'option « schema » (propre à
        Prisma, ajoutée par certains environnements) que psycopg refuse."""
        morceaux = urlsplit(self.database_url.replace("postgresql://", "postgresql+psycopg://", 1))
        options = [(cle, valeur) for cle, valeur in parse_qsl(morceaux.query) if cle != "schema"]
        return urlunsplit(morceaux._replace(query=urlencode(options)))


reglages = Reglages()
