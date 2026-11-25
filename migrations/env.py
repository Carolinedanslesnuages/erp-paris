"""Environnement Alembic : l'adresse de la base vient de la configuration de l'application."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.base import Base
from app.config import reglages

configuration = context.config
if configuration.config_file_name is not None:
    fileConfig(configuration.config_file_name)
configuration.set_main_option("sqlalchemy.url", reglages.adresse_base)
target_metadata = Base.metadata


def migrer() -> None:
    connectable = engine_from_config(
        configuration.get_section(configuration.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connexion:
        context.configure(connection=connexion, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


migrer()
