"""Beam Model."""
import json

import sqlalchemy as sa
import sqlalchemy.orm as so

from .db import BaseModel


class Beam(BaseModel):
    """Beam."""

    __tablename__ = "beams"

    id: so.Mapped[int] = so.mapped_column(primary_key=True, autoincrement=True)
    name: so.Mapped[str | None] = so.mapped_column(sa.String(32), index=True)
    description: so.Mapped[str | None] = so.mapped_column(sa.String(128))
    length: so.Mapped[float] = so.mapped_column(sa.Float)
    coordinates: so.Mapped[str] = so.mapped_column(sa.String)

    # foreign keys
    project_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("projects.id", ondelete="CASCADE"))

    # relationships
    project: so.Mapped["Project"] = so.relationship(back_populates="beams")  # noqa: F821
    # beam_loads: so.Mapped[list["BeamLoad"]] = so.relationship(  # noqa: F821
    #     cascade="all, delete", back_populates="beam"
    # )

    __table_args__ = (sa.CheckConstraint("length > 0", name="check_length_positive"),)

    def set_coordinates(self, coords_list: list[tuple[float, float]]) -> None:
        """Set coordinates."""
        self.coordinates = json.dumps(coords_list)

    def get_coordinates(self) -> list[tuple[float, float]]:
        """Get coordinates."""
        return json.loads(self.coordinates)

    def area(self) -> float:
        """Calculate and return the beam's cross-sectional area using the Shoelace formula.

        This method uses the Shoelace formula to calculate the area of a polygon
        defined by the coordinates of its vertices. The coordinates should be
        ordered either clockwise or counterclockwise.

        Note:
            The coordinates should be set using the `set_coordinates` or `get_coordinates`
            methods before calling this function.

        Returns:
            float: The computed area of the beam's cross-sectional shape.
        """
        area = 0
        coordinates = self.get_coordinates()
        n = len(coordinates)

        for i in range(n):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[(i + 1) % n]  # % n para volver al principio al llegar al último vértice
            area += (x1 * y2) - (x2 * y1)

        return abs(area) / 2.0

    def volume(self) -> float:
        """Calculate the beam's volume.

        Returns:
            float: The volume of the beam.
        """
        return self.area() * self.length

    def weight(self, concrete_density: float = 2.5) -> float:
        """Calculate the beam's weight.

        Args:
            concrete_density (float, optional): The beam's concrete density in Ton/m³. Defaults to 2.5.

        Returns:
            float: The weight of the beam in tons, based on the calculated volume in cubic meters and the provided
                concrete density.
        """
        if concrete_density <= 0:
            raise ValueError(f"Concrete density must be greather than 0 {concrete_density=}")

        return self.volume() * concrete_density

    def __str__(self) -> str:
        """Return a string representation of the beam.

        Returns:
            str: The string representation of the beam.
        """
        name = f" - {self.name}" if self.name is not None else ""
        return f"B{self.id:03}{name}"
