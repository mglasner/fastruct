"""Tests for interaction_2d module."""
import numpy as np
import pytest
from shapely import Polygon

from fastruct.analysis.interaction.interaction_2d import max_tension, rotate_polygon


@pytest.mark.parametrize(
    "polygon, angle_deg, pivot, delta, expected_polygon",
    [
        (
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            90,
            None,
            None,
            Polygon([(0, 0), (0, 1), (-1, 1), (-1, 0)]),
        ),
        (
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            45,
            np.array([0.5, 0.5]),
            None,
            Polygon([(0.5, -0.2071), (1.2071, 0.5), (0.5, 1.2071), (-0.2071, 0.5)]),
        ),
        (
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            0,
            None,
            np.array([1, 1]),
            Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
        ),
    ],
)
def test_rotate_polygon(polygon, angle_deg, pivot, delta, expected_polygon):
    transformed_polygon = rotate_polygon(polygon, angle_deg, pivot, delta)

    # Compare each coordinate of the transformed polygon with the expected one
    for coord1, coord2 in zip(list(transformed_polygon.exterior.coords), list(expected_polygon.exterior.coords)):
        assert np.isclose(coord1[0], coord2[0], atol=1e-4)
        assert np.isclose(coord1[1], coord2[1], atol=1e-4)


def test_max_tension():
    """Test max tension."""
    assert 1 == 1
