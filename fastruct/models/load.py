"""Load Model."""
import sqlalchemy as sa
import sqlalchemy.orm as so

from .db import BaseModel


class Load(BaseModel):
    """Load."""

    __tablename__ = "loads"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    p: so.Mapped[float] = so.mapped_column(sa.Float)
    vx: so.Mapped[float] = so.mapped_column(sa.Float)
    vy: so.Mapped[float] = so.mapped_column(sa.Float)
    mx: so.Mapped[float] = so.mapped_column(sa.Float)
    my: so.Mapped[float] = so.mapped_column(sa.Float)

    foundation_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("foundations.id", ondelete="CASCADE"))
    foundation: so.Mapped["Foundation"] = so.relationship(back_populates="loads")  # noqa: F821

    user_load_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user_loads.id", ondelete="CASCADE"))
    user_load: so.Mapped["UserLoad"] = so.relationship(back_populates="load")  # noqa: F821

    def as_list(self):
        """List serialization."""
        return [self.p, self.vx, self.vy, self.mx, self.my]

    def __str__(self) -> str:
        """Return a string representation of the foundation.

        Returns:
            str: The string representation of load.
        """
        return f"Load id: {self.id}"
