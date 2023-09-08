"""Foundation model tests."""
from random import randint

import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from ..foundation import Foundation
from ..project import Project
from .fixtures import engine, foundation1, project1, session


def test_create_foundation(session: Session, foundation1: Foundation):
    """Create an instance in database."""
    foundations = session.query(Foundation).all()
    foundation = foundations[0]
    assert len(foundations) == 1
    assert foundation.project_id == 1
    assert foundation.lx == foundation1.lx == 1
    assert foundation.ly == foundation1.ly == 1
    assert foundation.lz == foundation1.lz == 1
    assert foundation.depth == foundation1.depth == 1
    assert foundation.name == foundation1.name == "my foundation"
    assert foundation.description == foundation1.description == "my description"
    assert foundation.area() == foundation1.area() == 1
    assert foundation.column_area() == foundation1.column_area() == 0.0225
    assert foundation.volume() == foundation1.volume() == 1
    assert foundation.inertia()[0] == foundation1.inertia()[0] == pytest.approx(1 / 12, 1e-9)
    assert foundation.inertia()[1] == foundation1.inertia()[1] == pytest.approx(1 / 12, 1e-9)
    assert foundation.weight(concrete_density=2.5) == foundation1.weight(concrete_density=2.5) == 2.5
    assert foundation.ground_weight(ground_density=1.6) == foundation1.ground_weight(ground_density=1.6) == 0
    assert str(foundation) == str(foundation1) == "F001 - my foundation: Lx=1.00 Ly=1.00 Lz=1.00"


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
    "lx, ly, lz, concrete_density, expected_weight",
    [
        (10.0, 5.0, 2.0, 2.5, 250.0),
        (5.00, 5.0, 5.0, 2.5, 312.5),
        (2.00, 3.0, 4.0, 2.5, 60.00),
        (10.0, 5.0, 2.0, 1.0, 100.0),
        (5.00, 5.0, 5.0, 2.0, 250.0),
        (2.00, 3.0, 4.0, 3.0, 72.0),
    ],
)
def test_foundation_weight(lx: float, ly: float, lz: float, concrete_density: float, expected_weight: float) -> None:
    """Test foundation weight calculation.

    This test verifies that the weight calculation is accurate for various test cases.

    Args:
        lx: Length along the X dimension of the foundation.
        ly: Length along the Y dimension of the foundation.
        lz: Length along the Z dimension of the foundation.
        concrete_density (float): The foundation's concrete density in Ton/m³.
        expected_weight: Expected weight for the given dimensions.
    """
    foundation = Foundation(lx=lx, ly=ly, lz=lz, depth=lz)
    assert foundation.weight(concrete_density=concrete_density) == expected_weight


def test_negative_density_raises_value_error():
    """Test that a negative concrete density raises a ValueError."""
    foundation = Foundation(lx=1, ly=1, lz=1, depth=1)
    with pytest.raises(ValueError) as excinfo:
        foundation.weight(concrete_density=-1)

    assert "Concrete density must be greather than 0" in str(excinfo.value)


def test_zero_density_raises_value_error():
    """Test that a zero concrete density raises a ValueError."""
    foundation = Foundation(lx=1, ly=1, lz=1, depth=1)
    with pytest.raises(ValueError) as excinfo:
        foundation.weight(concrete_density=0)

    assert "Concrete density must be greather than 0" in str(excinfo.value)


@pytest.mark.parametrize(
    "lx, ly, lz, depth, col_x, col_y, ground_density, expected_weight",
    [
        (10.0, 5.0, 2.0, 3.0, 0.5, 0.5, 1.6, 79.60),
        (5.00, 5.0, 5.0, 6.0, 1.0, 1.0, 1.6, 38.40),
        (2.00, 3.0, 4.0, 5.0, 0.2, 0.2, 1.6, 9.536),
        (10.0, 5.0, 2.0, 2.5, 2.0, 2.0, 2.0, 46.00),
        (5.00, 5.0, 5.0, 6.5, 1.0, 0.5, 1.0, 36.75),
        (2.00, 3.0, 4.0, 4.5, 0.0, 0.0, 3.0, 9.000),
    ],
)
def test_ground_weight(
    lx: float,
    ly: float,
    lz: float,
    depth: float,
    col_x: float,
    col_y: float,
    ground_density: float,
    expected_weight: float,
) -> None:
    """Test ground weight calculation.

    This test verifies that the weight calculation is accurate for various test cases, including different column dimensions.

    Args:
        lx: Length along the X dimension of the foundation.
        ly: Length along the Y dimension of the foundation.
        lz: Length along the Z dimension of the foundation.
        depth: Foundation depth.
        col_x: Column length along the X dimension.
        col_y: Column length along the Y dimension.
        ground_density: Ground density.
        expected_weight: Expected weight for the given dimensions.
    """
    foundation = Foundation(lx=lx, ly=ly, lz=lz, depth=depth, col_x=col_x, col_y=col_y)
    assert foundation.ground_weight(ground_density=ground_density) == pytest.approx(expected_weight, rel=1e-5)


def test_negative_ground_density_raises_value_error() -> None:
    """Test that a negative ground density raises a ValueError."""
    foundation = Foundation(lx=1, ly=1, lz=1, depth=2)
    with pytest.raises(ValueError) as excinfo:
        foundation.ground_weight(ground_density=-1)

    assert "Ground density must be greather than 0" in str(excinfo.value)


def test_zero_ground_density_raises_value_error() -> None:
    """Test that a zero ground density raises a ValueError."""
    foundation = Foundation(lx=1, ly=1, lz=1, depth=2)
    with pytest.raises(ValueError) as excinfo:
        foundation.ground_weight(ground_density=0)

    assert "Ground density must be greather than 0" in str(excinfo.value)


def test_lx_constraint(session: Session, project1: Project):
    """Test lx constraint."""
    invalid_foundation = Foundation(
        project_id=project1.id, lx=-1, ly=1, lz=1, depth=1, ex=0, ey=0, col_x=0.1, col_y=0.1
    )
    session.add(invalid_foundation)
    with pytest.raises(IntegrityError) as e:
        session.commit()
    assert "ck_foundations_check_lx_positive" in str(e.value)
    session.rollback()


def test_ly_constraint(session: Session, project1: Project):
    """Test ly constraint."""
    invalid_foundation = Foundation(
        project_id=project1.id, lx=1, ly=-1, lz=1, depth=1, ex=0, ey=0, col_x=0.1, col_y=0.1
    )
    session.add(invalid_foundation)
    with pytest.raises(IntegrityError) as e:
        session.commit()
    assert "ck_foundations_check_ly_positive" in str(e.value)
    session.rollback()


def test_lz_constraint(session: Session, project1: Project):
    """Test lz constraint."""
    invalid_foundation = Foundation(
        project_id=project1.id, lx=1, ly=1, lz=-1, depth=1, ex=0, ey=0, col_x=0.1, col_y=0.1
    )
    session.add(invalid_foundation)
    with pytest.raises(IntegrityError) as e:
        session.commit()
    assert "ck_foundations_check_lz_positive" in str(e.value)
    session.rollback()


def test_col_x_constraint(session: Session, project1: Project):
    """Test col_x constraint."""
    invalid_foundation = Foundation(
        project_id=project1.id, lx=1, ly=1, lz=1, depth=1, ex=0, ey=0, col_x=-0.1, col_y=0.1
    )
    session.add(invalid_foundation)
    with pytest.raises(IntegrityError) as e:
        session.commit()
    assert "ck_foundations_check_col_x_positive" in str(e.value)
    session.rollback()


def test_col_y_constraint(session: Session, project1: Project):
    """Test col_y constraint."""
    invalid_foundation = Foundation(
        project_id=project1.id, lx=1, ly=1, lz=1, depth=1, ex=0, ey=0, col_x=0.1, col_y=-0.1
    )
    session.add(invalid_foundation)
    with pytest.raises(IntegrityError) as e:
        session.commit()
    assert "ck_foundations_check_col_y_positive" in str(e.value)
    session.rollback()


def test_depth_constraint(session: Session, project1: Project):
    """Test depth constraint."""
    invalid_foundation = Foundation(
        project_id=project1.id, lx=1, ly=1, lz=1, depth=-1, ex=0, ey=0, col_x=0.1, col_y=0.1
    )
    session.add(invalid_foundation)
    with pytest.raises(IntegrityError) as e:
        session.commit()
    assert "ck_foundations_check_depth_positive" in str(e.value)
    session.rollback()


def test_depth_greater_lz_constraint(session: Session, project1: Project):
    """Test lz and depth constraint."""
    invalid_foundation = Foundation(project_id=project1.id, lx=1, ly=1, lz=2, depth=1, ex=0, ey=0, col_x=0.1, col_y=0.1)
    session.add(invalid_foundation)
    with pytest.raises(IntegrityError) as e:
        session.commit()
    assert "ck_foundations_check_depth_greater_lz" in str(e.value)
    session.rollback()
