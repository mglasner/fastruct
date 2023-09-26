"""Tests for interaction_2d module."""
import numpy as np
import pytest

from fastruct.analysis.interaction.interaction_2d import max_tension, rotate_coordinates


@pytest.mark.parametrize(
    "coordinates, angle_deg, pivot, delta, expected_result",
    [
        (
            np.array([(0, 0), (1, 0), (1, 1), (0, 1)]),
            90,
            None,
            None,
            np.array([(0, 0), (0, 1), (-1, 1), (-1, 0)]),
        ),
        (
            np.array([(0, 0), (1, 0), (1, 1), (0, 1)]),
            45,
            np.array([0.5, 0.5]),
            None,
            np.array([(0.5, -0.2071), (1.2071, 0.5), (0.5, 1.2071), (-0.2071, 0.5)]),
        ),
        (
            np.array([(0, 0), (1, 0), (1, 1), (0, 1)]),
            0,
            None,
            np.array([1, 1]),
            np.array([(1, 1), (2, 1), (2, 2), (1, 2)]),
        ),
    ],
)
def test_rotate_coordinates(coordinates, angle_deg, pivot, delta, expected_result):
    """Test rotate coordinates."""
    result = rotate_coordinates(coordinates, angle_deg, pivot, delta)
    np.testing.assert_array_almost_equal(result, expected_result, decimal=4)
