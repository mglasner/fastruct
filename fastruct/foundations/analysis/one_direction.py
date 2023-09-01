"""Foundation one direction analysis."""
from fastruct.models.foundation import Foundation
from fastruct.models.load import Load


def one_direction_analysis(
    foundation: Foundation,
) -> tuple[list[tuple[float | None, float | None]], list[tuple[float, float]]]:
    """Returns maximun stresses and support percentaje by directions x and y."""
    percentajes = [get_percentaje_by_direction(foundation, load) for load in foundation.loads]
    all_stresses = [get_stress_by_direction(foundation, load) for load in foundation.loads]
    stresses = [(max_x, max_y) for max_x, _, max_y, _ in all_stresses]

    return stresses, percentajes


def get_stress_by_direction(
    foundation: Foundation, load: Load
) -> tuple[float | None, float | None, float | None, float | None]:
    """Get the stress for directions x, y."""
    max_x, min_x = compute_stress(load.p, load.my, foundation.lx, foundation.ly)
    max_y, min_y = compute_stress(load.p, load.mx, foundation.ly, foundation.lx)
    return max_x, min_x, max_y, min_y


def get_percentaje_by_direction(foundation: Foundation, load: Load) -> tuple[float, float]:
    """Get the lifting percentaje for directions x, y."""
    percentaje_x = compute_percentaje(load.p, load.my, foundation.lx)
    percentaje_y = compute_percentaje(load.p, load.mx, foundation.ly)
    return percentaje_x, percentaje_y


def compute_stress(axial: float, moment: float, width: float, length: float) -> tuple[float | None, float | None]:
    """Compute max and min stress."""
    if width <= 0:
        raise ValueError("width can't be negative nor zero.")

    if length <= 0:
        raise ValueError("length can't be negative nor zero.")

    sigma_max, sigma_min = None, None
    excentricity = abs(moment / axial)
    if is_trapezoidal_distribution(axial, moment, width):
        axial_stress = axial / (width * length)
        sigma_max = axial_stress * (1 + 6 * excentricity / width)
        sigma_min = axial_stress * (1 - 6 * excentricity / width)
    elif is_triangular_distribution(axial, moment, width):
        sigma_max = (2 * axial) / (3 * length * (width / 2 - excentricity))
        sigma_min = 0

    return sigma_max, sigma_min


def compute_percentaje(axial: float, moment: float, width: float) -> float:
    """Compute lifting percentaje."""
    if is_trapezoidal_distribution(axial, moment, width):
        return 100

    elif is_triangular_distribution(axial, moment, width):
        excentricity = abs(moment / axial)
        compressed_width = compressed_width_for_triangular_distribution(width, excentricity)
        return 0 if compressed_width <= 0 else compressed_width / width * 100

    return 0


def is_trapezoidal_distribution(axial: float, moment: float, width: float) -> bool:
    """Check if stress distributions is in trapezoidal shape for the loads given."""
    if width <= 0:
        raise ValueError("width can't be negative.")

    return False if axial <= 0 else abs(moment / axial) <= width / 6


def is_triangular_distribution(axial: float, moment: float, width: float) -> bool:
    """Check if stress distributions is in triangular shape for the loads given."""
    if width <= 0:
        raise ValueError("width can't be negative.")

    return False if axial <= 0 else width / 6 < abs(moment / axial) <= width / 4


def compressed_width_for_triangular_distribution(width: float, excentricity: float) -> float:
    """Compute compressed width."""
    return 3 * (width / 2 - excentricity)
