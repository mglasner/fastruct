"""Test para el modelo de Foundation."""
from random import randint
from typing import Literal

import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from ..foundation import Foundation
from .fixtures import engine, foundation_1_1_1, session


def test_create_foundation(session: Session, foundation_1_1_1: Foundation):
    """Create an instance in database."""
    fundaciones = session.query(Foundation).all()
    fundacion = fundaciones[0]
    assert len(fundaciones) == 1
    assert fundacion.lx == foundation_1_1_1.lx
    assert fundacion.ly == foundation_1_1_1.ly
    assert fundacion.lz == foundation_1_1_1.lz
    assert fundacion.depth == foundation_1_1_1.depth
    assert fundacion.name == foundation_1_1_1.name
    assert fundacion.description == foundation_1_1_1.description
    assert fundacion.lx == 1
    assert fundacion.ly == 1
    assert fundacion.lz == 1
    assert fundacion.depth == 1
    assert fundacion.name == "my foundation"
    assert fundacion.description == "my description"


@pytest.mark.parametrize(
    "lx,ly,lz,depth",
    [
        (0, 1, 1, 1),
        (1, 0, 1, 1),
        (1, 1, 0, 0),
        (-1, 1, 1, 1),
        (1, -1, 1, 1),
        (1, 1, -1, 1),
        (1, 1, 1, 0),
        (1, 1, 1, -1),
    ],
)
def test_foundation_invalid_values(session: Session, lx: float, ly: float, lz: float, depth: float) -> None:
    """Invalid values on creation."""
    with pytest.raises(IntegrityError):
        fundacion = Foundation(lx=lx, ly=ly, lz=lz, depth=depth)
        session.add(fundacion)
        session.commit()


@pytest.mark.parametrize(
    "lx,ly,lz,depth",
    [
        ("a", 1, 1, 1),
        (1, "b", 1, 1),
        (1, 1, "c", 1),
        (1, 1, 1, "d"),
    ],
)
def test_fundacion_invalid_string_values(session: Session, lx: str, ly: str, lz: str, depth: float) -> None:
    """Prueba la creación de instancias de la clase Foundation con valores de cadena."""
    with pytest.raises(StatementError, match="could not convert string to float"):
        fundacion = Foundation(lx=lx, ly=ly, lz=lz, depth=depth)
        session.add(fundacion)
        session.commit()


@pytest.mark.parametrize(
    "lx, ly, expected_area",
    [
        (10.0, 5.0, 50.0),
        (5.00, 5.0, 25.0),
        (2.00, 3.0, 6.00),
    ],
)
def test_foundation_area(lx: float, ly: float, expected_area: float) -> None:
    """Test foundation area calculation.

    This test verifies that the area calculation is accurate for various test cases.

    Args:
        lx: Length along the X dimension of the foundation.
        ly: Length along the Y dimension of the foundation.
        expected_area: Expected area for the given dimensions.
    """
    foundation = Foundation(lx=lx, ly=ly, lz=randint(1, 10), depth=randint(11, 20))
    assert foundation.area() == expected_area


@pytest.mark.parametrize(
    "lx, ly, lz, expected_volume",
    [
        (10.0, 5.0, 2.0, 100.0),
        (5.00, 5.0, 5.0, 125.0),
        (2.00, 3.0, 4.0, 24.00),
    ],
)
def test_foundation_volume(lx: float, ly: float, lz: float, expected_volume: float) -> None:
    """Test foundation volume calculation.

    This test verifies that the volume calculation is accurate for various test cases.

    Args:
        lx: Length along the X dimension of the foundation.
        ly: Length along the Y dimension of the foundation.
        lz: Length along the Z dimension of the foundation.
        expected_volume: Expected volume for the given dimensions.
    """
    foundation = Foundation(lx=lx, ly=ly, lz=lz, depth=lz)
    assert foundation.volume() == expected_volume


@pytest.mark.parametrize(
    "lx, ly, lz, expected_weight",
    [
        (10.0, 5.0, 2.0, 250.0),
        (5.00, 5.0, 5.0, 312.5),
        (2.00, 3.0, 4.0, 60.00),
    ],
)
def test_foundation_weight(lx: float, ly: float, lz: float, expected_weight: float) -> None:
    """Test foundation weight calculation.

    This test verifies that the weight calculation is accurate for various test cases.

    Args:
        lx: Length along the X dimension of the foundation.
        ly: Length along the Y dimension of the foundation.
        lz: Length along the Z dimension of the foundation.
        expected_weight: Expected weight for the given dimensions.
    """
    foundation = Foundation(lx=lx, ly=ly, lz=lz, depth=lz)
    assert foundation.weight() == expected_weight
