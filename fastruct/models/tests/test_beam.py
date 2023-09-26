"""Beam model tests."""
import json
from random import randint

import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from ..beam import Beam
from ..project import Project
from .fixtures import beam1, engine, project1, session


def test_create_beam(session: Session, beam1: Beam):
    """Create an instance in database."""
    beams = session.query(Beam).all()
    beam = beams[0]
    assert len(beams) == 1
    assert beam.project_id == 1
    assert beam.name == beam1.name == "my beam"
    assert beam.description == beam.description == "my beam description"
    assert beam.area() == beam1.area() == 1
    assert beam.volume() == beam1.volume() == 1
    assert beam.weight(concrete_density=2.5) == beam1.weight(concrete_density=2.5) == 2.5
    assert str(beam) == str(beam1) == "B001 - my beam"


@pytest.mark.parametrize(
    "coordinates, expected_area",
    [
        ([(-0.5, -1), (0.5, -1), (0.5, 1), (-0.5, 1)], 2),  # rectangle 1x2
        ([(-1, -0.5), (1, -0.5), (1, 0.5), (-1, 0.5)], 2),  # rectangle 2x1
        ([(-0.1, -0.4), (0.1, -0.4), (0.1, 0.4), (-0.1, 0.4)], 0.16),  # rectangle 0.2x0.8
    ],
)
def test_beam_area(coordinates: list[list[float]], expected_area: float) -> None:
    """Test beam area calculation.

    This test verifies that the area calculation is accurate for various test cases.

    Args:
        coordinates: Cross sectional coordinates.
        expected_area: Expected area for the given dimensions.
    """
    beam = Beam(length=1, coordinates=json.dumps(coordinates))
    assert beam.area() == pytest.approx(expected_area, rel=1e-9)
