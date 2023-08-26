"""Foundation Model."""
import sqlalchemy as sa
import sqlalchemy.orm as so

from .db import BaseModel


class Foundation(BaseModel):
    """Foundation."""

    __tablename__ = "foundations"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    name: so.Mapped[str | None] = so.mapped_column(sa.String(32), index=True)
    description: so.Mapped[str | None] = so.mapped_column(sa.String(128))
    lx: so.Mapped[float] = so.mapped_column(sa.Float)
    ly: so.Mapped[float] = so.mapped_column(sa.Float)
    lz: so.Mapped[float] = so.mapped_column(sa.Float)
    depth: so.Mapped[float] = so.mapped_column(sa.Float)

    loads: so.Mapped[list["Load"]] = so.relationship(cascade="all, delete", back_populates="foundation")  # noqa: F821
    user_loads: so.Mapped[list["UserLoad"]] = so.relationship(  # noqa: F821
        cascade="all, delete", back_populates="foundation"
    )

    __table_args__ = (
        sa.CheckConstraint("lx > 0", name="check_lx_positive"),
        sa.CheckConstraint("ly > 0", name="check_ly_positive"),
        sa.CheckConstraint("lz > 0", name="check_lz_positive"),
        sa.CheckConstraint("depth >= 0", name="check_depth_positive"),
        sa.CheckConstraint("depth >= lz", name="check_depth_greater_lz"),
    )

    def area(self) -> float:
        """Calculate the foundation's area.

        Returns:
            float: The area of the foundation.
        """
        return self.lx * self.ly

    def volume(self) -> float:
        """Calculate the foundation's volume.

        Returns:
            float: The volume of the foundation.
        """
        return self.lx * self.ly * self.lz

    def weight(self, concrete_density: float = 2.5) -> float:
        """Calculate the foundation's weight.

        Args:
            concrete_density (float, optional): The foundation's concrete density in Ton/m³. Defaults to 2.5.

        Returns:
            float: The weight of the foundation in tons, based on the calculated volume in cubic meters and the provided
                concrete density.
        """
        return self.volume() * concrete_density

    def ground_weight(self, ground_density: float = 2.0) -> float:
        """Calculate the weight of the ground above the foundation.

        Args:
            ground_density (float, optional): The ground's density in Ton/m³. Defaults to 2.0.

        Returns:
            float: The weight of the ground in tons, based on the calculated area in square meters, ground height,
                and the provided ground density.
        """
        ground_height = self.lz if self.depth is None else (self.depth - self.lz)
        return self.area() * ground_height * ground_density

    def __str__(self) -> str:
        """String representation of the foundation.

        The representation includes the ID (with zeros as a prefix to form numbers up to 999),
        and the foundation's dimensions, always displayed with two decimal places.
        If the name is not None, it will be included in the representation.

        Returns:
            str: The string representation of the foundation.
        """
        name = f"-{self.name}" if self.name is not None else ""
        return f"F{self.id:03}{name}: Lx={self.lx:.2f} Ly={self.ly:.2f} Lz={self.lz:.2f} Depth={self.depth:.2f}"
