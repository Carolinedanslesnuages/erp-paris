"""Accès à la base PostgreSQL (SQLAlchemy 2). Une session par requête, fermée à la fin."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import reglages

moteur = create_engine(reglages.adresse_base, pool_pre_ping=True)
FabriqueSession = sessionmaker(bind=moteur, autoflush=False)


class Base(DeclarativeBase):
    """Classe mère des tables : toute évolution passe par une migration Alembic."""


def session_base() -> Iterator[Session]:
    """Dépendance FastAPI : `session: Session = Depends(session_base)`."""
    with FabriqueSession() as session:
        yield session
