"""Project Model."""
import sqlalchemy as sa
import sqlalchemy.orm as so

from .db import BaseModel


class Project(BaseModel):
    """Project."""

    __tablename__ = "projects"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    name: so.Mapped[str | None] = so.mapped_column(sa.String(32), index=True)
    code: so.Mapped[str | None] = so.mapped_column(sa.String(32), index=True)
    description: so.Mapped[str | None] = so.mapped_column(sa.String(128))

    foundations: so.Mapped[list["Foundation"]] = so.relationship(
        cascade="all, delete", back_populates="project"
    )  # noqa: F821

    def __str__(self) -> str:
        """Return a string representation of project.

        Returns:
            str: The string representation of the foundation.
        """
        return f"Project '{self.name}', code '{self.code}'"
