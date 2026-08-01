"""
app/database/base.py
─────────────────────
SQLAlchemy 2.0 declarative base with explicit naming conventions.
All models must inherit from Base defined here.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

# Explicit naming conventions prevent Alembic from generating unnamed
# constraints, which causes issues on constraint renames and drops.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    Provides automatic __tablename__ generation and naming convention metadata.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """
        Automatically generate snake_case table names from class names.
        Example: TokenModel → token_model
        """
        import re

        name = cls.__name__
        # Remove trailing 'Model' suffix if present
        name = re.sub(r"Model$", "", name)
        # Convert CamelCase to snake_case
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def model_dump(self) -> dict[str, Any]:
        """
        Return a dictionary representation of this model instance.
        Useful for logging and debugging.
        """
        return {
            col.name: getattr(self, col.name)
            for col in self.__table__.columns  # type: ignore[attr-defined]
        }
