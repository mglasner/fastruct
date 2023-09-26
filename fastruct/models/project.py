"""Project Model."""
import sqlalchemy as sa
import sqlalchemy.orm as so

from .db import BaseModel


class Project(BaseModel):
    """Project."""

    __tablename__ = "projects"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), index=True)
    code: so.Mapped[str] = so.mapped_column(sa.String(32), index=True)
    description: so.Mapped[str | None] = so.mapped_column(sa.String(128))
    is_active: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)

    foundations: so.Mapped[list["Foundation"]] = so.relationship(  # noqa: F821
        cascade="all, delete", back_populates="project"
    )

    beams: so.Mapped[list["Beam"]] = so.relationship(cascade="all, delete", back_populates="project")  # noqa: F821

    def __str__(self) -> str:
        """Return a string representation of project.

        Returns:
            str: The string representation of the foundation.
        """
        return f"Project '{self.name}', code '{self.code}'"
