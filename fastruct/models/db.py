"""Sqlalchemy classes and instances."""
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """Base Model."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), server_default=sa.sql.func.now())
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), server_default=sa.sql.func.now(), onupdate=sa.sql.func.now()
    )

    def as_dict(self) -> dict:
        """Serialize model."""
        data = {f.name: getattr(self, f.name) for f in self.__table__.columns}

        # Datetimes as timestamps
        if "created_at" in data:
            data["created_at"] = round(data["created_at"].timestamp())

        if "updated_at" in data:
            data["updated_at"] = round(data["updated_at"].timestamp())

        return data
