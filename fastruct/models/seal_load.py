"""Load Model."""
import sqlalchemy as sa
import sqlalchemy.orm as so

from .db import BaseModel


class SealLoad(BaseModel):
    """SealLoad."""

    __tablename__ = "seal_loads"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    p: so.Mapped[float] = so.mapped_column(sa.Float)
    vx: so.Mapped[float] = so.mapped_column(sa.Float)
    vy: so.Mapped[float] = so.mapped_column(sa.Float)
    mx: so.Mapped[float] = so.mapped_column(sa.Float)
    my: so.Mapped[float] = so.mapped_column(sa.Float)

    # foreign keys
    foundation_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("foundations.id", ondelete="CASCADE"))
    user_load_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user_loads.id", ondelete="CASCADE"))

    # relationships
    foundation: so.Mapped["Foundation"] = so.relationship(back_populates="seal_loads")  # noqa: F821
    user_load: so.Mapped["UserLoad"] = so.relationship(back_populates="seal_load")  # noqa: F821

    def as_list(self):
        """List serialization."""
        return [self.p, self.vx, self.vy, self.mx, self.my]

    def __str__(self) -> str:
        """Return a string representation of the seal load.

        Returns:
            str: The string representation of load.
        """
        return f"Seal load id: {self.id}"
