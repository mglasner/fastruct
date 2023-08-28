"""Foundations design module."""
from models.foundation import Foundation
from models.load import Load

from .analysis.bi_direction import compressed_width_for_triangular_distribution, compute_stress


def get_ultimate_moments(
    foundation: Foundation,
) -> list[tuple[tuple[float | None, float | None], tuple[float | None, float | None]]]:
    """Ultimate moment for every load on foundation."""
    return [ultimate_moment_by_direction(foundation, load) for load in foundation.loads]


def ultimate_moment_by_direction(
    foundation: Foundation, load: Load
) -> tuple[tuple[float | None, float | None], tuple[float | None, float | None]]:
    """Compute the ultimate moment for foundation by direction."""
    sigma_max_x, sigma_min_x = compute_stress(load.p, load.my, foundation.lx, foundation.ly)
    sigma_max_y, sigma_min_y = compute_stress(load.p, load.mx, foundation.ly, foundation.lx)
    is_sigma_max_x_right = load.my >= 0
    is_sigma_max_y_right = load.mx >= 0
    return (
        ultimate_moments_by_side(
            sigma_max_x,
            sigma_min_x,
            is_sigma_max_x_right,
            foundation.ly,
            foundation.lx,
            foundation.col_x,
            foundation.ex,
            abs(load.my / load.p),
        ),
        ultimate_moments_by_side(
            sigma_max_y,
            sigma_min_y,
            is_sigma_max_y_right,
            foundation.lx,
            foundation.ly,
            foundation.col_y,
            foundation.ey,
            abs(load.mx / load.p),
        ),
    )


def ultimate_moments_by_side(
    sigma_max: float | None,
    sigma_min: float | None,
    is_sigma_max_right: bool,
    width: float,
    length: float,
    column_length: float,
    column_excentricity: float,
    load_excentricity: float,
) -> tuple[float | None, float | None]:
    # sourcery skip: assign-if-exp, merge-else-if-into-elif
    """Compute ultimate moment to the left and rigth."""
    length_left = length / 2 + column_excentricity - column_length / 2
    length_right = length - length_left - column_length
    if is_sigma_max_right:
        if sigma_min == 0:
            compressed_legth = compressed_width_for_triangular_distribution(length, load_excentricity)
            sigma_min_on_pivot = sigma_max * length_right / compressed_legth
        else:
            sigma_min_on_pivot = sigma_max * length_right / length

    else:
        if sigma_min == 0:
            compressed_legth = compressed_width_for_triangular_distribution(length, load_excentricity)
            sigma_min_on_pivot = sigma_max * length_left / compressed_legth
        else:
            sigma_min_on_pivot = sigma_max * length_left / length

    return (
        ultimate_moment(sigma_max, sigma_min_on_pivot, width, length_left),
        ultimate_moment(sigma_max, sigma_min_on_pivot, width, length_right),
    )


def ultimate_moment(sigma_max: float | None, sigma_min: float | None, width: float, length: float) -> float | None:
    """Compute the ultimate moment.

    Tension distribution must be always trapezoydal.
    """
    if sigma_max is None or sigma_min is None:
        return None
    if sigma_min < 0:
        return None

    return (sigma_max - sigma_min) * length**2 * width / 3 + sigma_min * length**2 * width / 2
