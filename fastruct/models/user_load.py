"""User Load Model."""
import sqlalchemy as sa
import sqlalchemy.orm as so

from .db import BaseModel


class UserLoad(BaseModel):
    """UserLoad."""

    __tablename__ = "user_loads"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    name: so.Mapped[str | None] = so.mapped_column(sa.String(32), index=True)
    p: so.Mapped[float] = so.mapped_column(sa.Float)
    vx: so.Mapped[float] = so.mapped_column(sa.Float)
    vy: so.Mapped[float] = so.mapped_column(sa.Float)
    mx: so.Mapped[float] = so.mapped_column(sa.Float)
    my: so.Mapped[float] = so.mapped_column(sa.Float)

    foundation_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("foundations.id", ondelete="CASCADE"))
    foundation: so.Mapped["Foundation"] = so.relationship(back_populates="user_loads")  # noqa: F821
    seal_load: so.Mapped["SealLoad"] = so.relationship(back_populates="user_load")  # noqa: F821

    def as_list(self):
        """List serialization."""
        return [self.p, self.vx, self.vy, self.mx, self.my]

    def __str__(self) -> str:
        """Representation of load as string.

        Returns:
            str: The string representation of load.
        """
        return f"User Load id: {self.id}"
