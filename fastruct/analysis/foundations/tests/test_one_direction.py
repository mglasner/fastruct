"""Tests for one-direction module."""
import pytest

from fastruct.analysis.foundations.one_direction import (
    compressed_width_for_triangular_distribution,
    compute_stress,
    is_trapezoidal_distribution,
    is_triangular_distribution,
)


@pytest.mark.parametrize(
    "axial, moment, width",
    [(1, 1, 6), (1, -1, 6), (10, 1, 6), (10, -1, 6), (1, 0.1, 6), (1, -0.1, 6), (1, 1, 60), (1, -1, 60)],
)
def test_is_trapezoidal_distribution(axial, moment, width) -> None:
    """Test is trapezoidal distribution."""
    assert is_trapezoidal_distribution(axial, moment, width)


@pytest.mark.parametrize(
    "axial, moment, width",
    [
        (-1, 1, 6),
        (-1, -1, 6),
        (0.1, 1, 6),
        (0.1, -1, 6),
        (1, 10, 6),
        (1, -10, 6),
        (1, 1, 1),
        (1, -1, 1),
        (0, -1, 6),
        (0, 10, 6),
        (0, -10, 6),
        (0, 1, 1),
        (0, -1, 1),
        (0, 1, 6),
        (0, 0.1, 6),
        (0, -0.1, 6),
        (0, 1, 60),
        (0, -1, 60),
    ],
)
def test_not_is_trapezoidal_distribution(axial, moment, width) -> None:
    """Test is trapezoidal distribution."""
    assert not is_trapezoidal_distribution(axial, moment, width)


@pytest.mark.parametrize(
    "axial, moment, width",
    [
        (1, 1, -0.6),
        (1, -1, -0.6),
        (10, 1, -0.6),
        (10, -1, -0.6),
        (1, 0.1, -0.6),
        (1, -0.1, -0.6),
        (1, 1, -6),
        (1, -1, -6),
        (10, 1, -6),
        (10, -1, -6),
        (1, 0.1, -6),
        (1, -0.1, -6),
        (1, 1, -60),
        (1, -1, -60),
        (10, 1, -60),
        (10, -1, -60),
        (1, 0.1, -60),
        (1, -0.1, -60),
    ],
)
def test_is_trapezoidal_distribution_raises(axial, moment, width) -> None:
    """Negative width in trapezoidal distribution."""
    with pytest.raises(ValueError, match="width can't be negative."):
        is_trapezoidal_distribution(axial, moment, width)


@pytest.mark.parametrize(
    "axial, moment, width",
    [
        (1, 1, 5.99),
        (1, -1, 5.99),
        (1, 1, 5),
        (1, -1, 5),
        (1, 1, 4),
        (1, -1, 4),
    ],
)
def test_is_triangular_distribution(axial, moment, width) -> None:
    """Test is triangular distribution."""
    assert is_triangular_distribution(axial, moment, width)


@pytest.mark.parametrize(
    "axial, moment, width",
    [
        (1, 1, 6),
        (1, -1, 6),
        (10, 1, 6),
        (10, -1, 6),
        (1, 1, 6.01),
        (1, -1, 6.01),
        (1, 1, 3.99),
        (1, -1, 3.99),
        (1, 0.1, 4),
        (1, 0.1, 4),
        (-1, 1, 6),
        (-1, -1, 6),
        (-10, 1, 6),
        (-10, -1, 6),
        (-1, 1, 6.01),
        (-1, -1, 6.01),
        (-1, 1, 3.99),
        (-1, -1, 3.99),
        (-1, 0.1, 4),
        (-1, 0.1, 4),
    ],
)
def test_not_is_triangular_distribution(axial, moment, width) -> None:
    """Test not is triangular distribution."""
    assert not is_triangular_distribution(axial, moment, width)


@pytest.mark.parametrize(
    "axial, moment, width",
    [
        (1, 1, -0.6),
        (1, -1, -0.6),
        (10, 1, -0.6),
        (10, -1, -0.6),
        (1, 0.1, -0.6),
        (1, -0.1, -0.6),
        (1, 1, -6),
        (1, -1, -6),
        (10, 1, -6),
        (10, -1, -6),
        (1, 0.1, -6),
        (1, -0.1, -6),
        (1, 1, -60),
        (1, -1, -60),
        (10, 1, -60),
        (10, -1, -60),
        (1, 0.1, -60),
        (1, -0.1, -60),
        (1, 1, -5.99),
        (1, -1, -5.99),
        (1, 1, -5),
        (1, -1, -5),
        (1, 1, -4),
        (1, -1, -4),
    ],
)
def test_is_triangular_distribution_raises(axial, moment, width) -> None:
    """Negative width in triangular distribution."""
    with pytest.raises(ValueError, match="width can't be negative."):
        is_triangular_distribution(axial, moment, width)


@pytest.mark.parametrize(
    "width, excentricity, expected",
    [
        (10.0, 5.0, 0),
        (10.0, 4.9, 0.3),
        (10.0, 5.1, 0),
        (10.0, 10.0, 0),
        (2, 0.35, 1.95),
        (2, 0.45, 1.65),
        (2, 0.99, 0.03),
        (2, 1, 0),
    ],
)
def test_compressed_width_for_triangular_distribution(width: float, excentricity: float, expected: float):
    """Test compressed_width_for_triangular_distribution function."""
    result = compressed_width_for_triangular_distribution(width, excentricity)
    assert result == pytest.approx(expected, rel=1e-9)


def test_compressed_width_for_negative_width():
    """Test compressed_width_for_triangular_distribution raises for negative width."""
    with pytest.raises(ValueError, match="width can't be negative."):
        compressed_width_for_triangular_distribution(-1.0, 5.0)


def test_compressed_width_for_excentricity_within_limit():
    """Test compressed_width_for_triangular_distribution raises for excentricity within limit."""
    with pytest.raises(ValueError, match="It is not triangular distribution."):
        compressed_width_for_triangular_distribution(10.0, 1.0)


@pytest.mark.parametrize("width,length", [(-1, 5), (0, 5), (5, -1), (5, 0)])
def test_compute_stress_invalid_values(width: float, length: float):
    """Test for invalid width and length."""
    with pytest.raises(ValueError, match="can't be negative nor zero."):
        compute_stress(50, 10, width, length)


@pytest.mark.parametrize(
    "axial,moment,width,length, expected_sigma_max, expected_sigma_min",
    [(1, 1, 6, 6, 1 / 18, 0), (1, -1, 6, 6, 1 / 18, 0), (10, 1, 6, 6, 11 / 36, 9 / 36)],
)
def test_compute_stress_trapezoidal(
    axial: float, moment: float, width: float, length: float, expected_sigma_max: float, expected_sigma_min: float
):
    """Test for trapezoidal distribution scenario."""
    sigma_max, sigma_min = compute_stress(axial, moment, width, length)
    assert expected_sigma_max == sigma_max
    assert expected_sigma_min == sigma_min


@pytest.mark.parametrize(
    "axial,moment,width,length, expected_sigma_max, expected_sigma_min",
    [
        (1, 1, 5, 5, 4 / 45, 0),
        (1, -1, 5, 5, 4 / 45, 0),
    ],
)
def test_compute_stress_triangular(
    axial: float, moment: float, width: float, length: float, expected_sigma_max: float, expected_sigma_min: float
):
    """Test for triangular distribution scenario."""
    sigma_max, sigma_min = compute_stress(axial, moment, width, length)
    assert expected_sigma_max == sigma_max
    assert expected_sigma_min == sigma_min
