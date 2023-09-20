"""2D MP interaction curve."""
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon

from fastruct.common.decorators import timer


@timer
def get_curve2d(coordinates: np.ndarray, reinforced_bars: np.ndarray) -> np.ndarray:
    """Compute the 2D interaction curve for axial force vs. bending moment.

    Args:
        coordinates (np.ndarray): The coordinates defining the Polygon section.
        reinforced_bars (np.ndarray): Array with properties of reinforcing bars.

    Returns:
        np.ndarray: Array of moments and axial forces in different configurations.
    """
    section = Polygon(coordinates)
    yi, diameters, yield_stress = reinforced_bars[:, 1], reinforced_bars[:, 2], reinforced_bars[:, 3]
    bars_area = diameters**2 * np.pi / 4

    # Compute positive moment capacities
    mp_min = max_tension(section, yi, bars_area, yield_stress)
    mp_pos = curve2d(section, reinforced_bars, 2500, 0.003)

    # Compute maximum axial compression capacity
    mp_max = max_compresion(section, bars_area, yield_stress, 2500)

    # Rotate section and reinforcing bars by 180 degrees for negative moment capacities
    rotated_coordinates = rotate_coordinates(coordinates, 180, pivot=None, delta=None)
    rotated_section = Polygon(rotated_coordinates)

    bar_coordinates = reinforced_bars[:, :2]
    rotated_bar_coordinates = rotate_coordinates(bar_coordinates, 180, pivot=None, delta=None)
    rotated_reinforced_bars = np.hstack((rotated_bar_coordinates, reinforced_bars[:, 2:]))

    mp_neg = curve2d(rotated_section, rotated_reinforced_bars, 2500, 0.003, is_neg=True)

    # return np.vstack((mp_max, mp_pos, mp_neg, mp_min))
    return np.vstack((mp_max, mp_pos, mp_min, mp_neg[::-1], mp_max))


@timer
def curve2d(
    section: Polygon,
    reinforced_bars: np.ndarray,
    concrete_strength: float,
    max_strain: float,
    num_points: int = 50,
    is_neg=False,
) -> np.ndarray:
    """Computes the interaction curve for a given 2D polygon section with reinforcement.

    Args:
        section (Polygon): The Shapely Polygon object representing the cross-section of the structural element.
        reinforced_bars (np.ndarray): A NumPy array containing the properties of the reinforcing bars.
        concrete_strength (float): The characteristic compressive strength of the concrete (fc).
        max_strain (float): The maximum unit strain in the concrete.
        num_points (int, optional): Number of points to be calculated in the interaction curve, default is 100.

    Returns:
        np.ndarray: An array containing the nominal moments and axial forces calculated for the section.
    """
    centroid_y = section.centroid.y
    ymax, ymin = section.bounds[3], section.bounds[1]
    dy = (ymax - ymin) / num_points

    bar_area = reinforced_bars[:, 2] ** 2 * np.pi / 4
    neutral_axis_height = np.arange(ymin, ymax - dy, dy)
    bar_y_position = reinforced_bars[:, 1][:, np.newaxis]

    strain = max_strain * (bar_y_position - neutral_axis_height) / (ymax - neutral_axis_height)
    bar_forces = bars_force(
        bar_area[:, np.newaxis], reinforced_bars[:, 3][:, np.newaxis], reinforced_bars[:, 4][:, np.newaxis], strain
    )

    concrete_moment = np.zeros(len(neutral_axis_height))
    concrete_force = np.zeros(len(neutral_axis_height))

    for i, neutral_axis in enumerate(neutral_axis_height):
        compression_edge = ymax - beta1(concrete_strength) * (ymax - neutral_axis)
        compressed_section = section.intersection(
            Polygon(
                [
                    (section.bounds[0], compression_edge),
                    (section.bounds[2], compression_edge),
                    (section.bounds[2], ymax),
                    (section.bounds[0], ymax),
                ]
            )
        )
        concrete_cg_y = compressed_section.centroid.y if compressed_section.is_valid else centroid_y
        compressed_bar_area = np.sum(bar_area[reinforced_bars[:, 1] > compression_edge])

        compressed_concrete_area = compressed_section.area - compressed_bar_area if compressed_section.is_valid else 0.0

        concrete_moment[i] = compressed_concrete_area * 0.85 * concrete_strength * (concrete_cg_y - centroid_y)
        concrete_force[i] = compressed_concrete_area * 0.85 * concrete_strength

    nominal_moments = np.sum(bar_forces * (reinforced_bars[:, 1][:, np.newaxis] - centroid_y), axis=0) + concrete_moment
    axial_forces = np.sum(bar_forces, axis=0) + concrete_force

    return np.column_stack((-1 * nominal_moments if is_neg else nominal_moments, axial_forces))


@timer
def max_tension(
    section: Polygon, y_bars: np.ndarray, bars_area: np.ndarray, bars_yield_stress: np.ndarray
) -> np.ndarray:
    """Computes the maximum tensile force for a given reinforced concrete section.

    Args:
        section (Polygon): A Shapely Polygon representing the concrete section.
        y_bars (np.ndarray): Y-coordinates of the centroids of the reinforcement bars.
        bars_area (np.ndarray): Cross-sectional areas of the reinforcement bars.
        bars_yield_stress (np.ndarray): Yield stress values of the reinforcement bars.

    Returns:
        np.ndarray: A 1D array containing the maximum tensile moment and axial stress.
    """
    ycg = section.centroid.y
    mmin = -np.sum(bars_area * bars_yield_stress * (y_bars - ycg))
    pmin = -np.sum(bars_area * bars_yield_stress)
    return np.array([mmin, pmin])


@timer
def max_compresion(section: Polygon, bars_area: np.ndarray, bars_yield_stress: np.ndarray, fc: float) -> np.ndarray:
    """Computes the maximum compressive force for a reinforced concrete section according to ACI318S-08.

    Args:
        section (Polygon): A Shapely Polygon representing the concrete section.
        bars_area (np.ndarray): Cross-sectional areas of the reinforcement bars.
        bars_yield_stress (np.ndarray): Yield stress values of the reinforcement bars.
        fc (float): Characteristic strength of the concrete.

    Returns:
        np.ndarray: A 1D array containing the maximum compressive moment and axial stress.
    """
    steel_area = np.sum(bars_area)
    force_by_steel_bar = bars_area * bars_yield_stress

    concrete_force = 0.85 * fc * (section.area - steel_area)
    steel_force = np.sum(force_by_steel_bar)
    total_force = concrete_force + steel_force

    return np.array([0, total_force])


def beta1(fc: float):
    """Valor de beta1 según ACI318S-08 pto. 10.2.7.3.

    Args:
        fc (int, float): Resistencia caracteristica del hormigón en ton/m2.

    Returns:
        (int, float): Beta1
    """
    lower_fc_limit = 1700
    fc_limit = 2800
    if fc < lower_fc_limit:
        print("fc lower than 17 MPa")

    return 0.85 if fc <= fc_limit else max(0.85 - 0.05 / 700 * (fc - 2800), 0.65)


@timer
def bars_force(area: np.ndarray, yield_stress: np.ndarray, elasticity_module: np.ndarray, es: np.ndarray) -> np.ndarray:
    """Computes the force in reinforcing bars based on their material properties and strain, in a batch-wise manner.

    This function takes in arrays representing the area, yield stress, elastic modulus, and strain of each reinforcing
    bar. It then computes the force in each bar according to its stress-strain relationship. The function handles
    both elastic and plastic behavior of the material.

    Args:
        area (np.ndarray): The cross-sectional area of the reinforcing bars.
        yield_stress (np.ndarray): The yield stress of the material for each bar.
        elasticity_module (np.ndarray): The elastic modulus (Young's modulus) of the material for each bar.
        es (np.ndarray): The strain in each reinforcing bar, a dimensionless quantity.

    Returns:
        np.ndarray: The resulting force in each bar.
    """
    condition = np.abs(es) <= yield_stress / elasticity_module
    force = np.where(condition, elasticity_module * es * area, yield_stress * area * np.sign(es))

    return force


@timer
def plot_curve2d(curve_data: np.ndarray, original_section: np.ndarray, original_bars: np.ndarray) -> None:
    """Plot the 2D interaction axial force vs. bending moment curve, along with the original section.

    Args:
        curve_data (np.ndarray): An array containing pairs of (M, P) for the curve.
        original_section (np.ndarray): Coordinates of the original section.
        original_bars (np.ndarray): Coordinates and properties of reinforcing bars in the original section.

    Returns:
        None
    """
    m, p = curve_data[:, 0], curve_data[:, 1]
    diameters = original_bars[:, 2]
    scaling_factor = 2000

    unique_diameters = np.unique(diameters)
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_diameters)))

    plt.figure(figsize=(15, 6))
    plt.subplot(1, 2, 1)
    plt.plot(m, p, label="M-P Curve", linewidth=2)
    plt.fill_between(m, p, color="skyblue", alpha=0.4)

    plt.axhline(0, color="black", linestyle="--", linewidth=2, label="P=0")
    plt.axvline(0, color="black", linestyle="--", linewidth=2, label="M=0")

    max_p, min_p = np.max(p), np.min(p)
    max_m, min_m = np.max(m), np.min(m)

    max_p_m_values = m[p == max_p]
    plt.scatter(max_p_m_values, [max_p] * len(max_p_m_values), color="red", zorder=5)
    plt.annotate(
        f"({int(max_p_m_values[0])}, {int(max_p)})",
        (max_p_m_values[0], max_p),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
    )

    min_p_m_values = m[p == min_p]
    plt.scatter(min_p_m_values, [min_p] * len(min_p_m_values), color="blue", zorder=5)
    plt.annotate(
        f"({int(min_p_m_values[0])}, {int(min_p)})",
        (min_p_m_values[0], min_p),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
    )

    plt.scatter([max_m, min_m], [p[m == max_m][0], p[m == min_m][0]], color="green", zorder=5)
    plt.annotate(
        f"({int(max_m)}, {int(p[m == max_m][0])})",
        (max_m, p[m == max_m][0]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
    )
    plt.annotate(
        f"({int(min_m)}, {int(p[m == min_m][0])})",
        (min_m, p[m == min_m][0]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
    )

    # Highlight points where P = 0
    zero_p_m_values = m[np.isclose(p, 0, atol=1e-6)]
    plt.scatter(zero_p_m_values, [0] * len(zero_p_m_values), color="orange", zorder=5)

    # Annotate points where P = 0
    for moment in zero_p_m_values:
        plt.annotate(f"({int(moment)}, 0)", (moment, 0), textcoords="offset points", xytext=(0, 10), ha="center")

    plt.xlabel("Bending Moment (M)")
    plt.ylabel("Axial Force (P)")
    plt.grid(True)
    plt.legend()

    ax = plt.subplot(1, 2, 2, aspect="equal")
    plt.fill(
        original_section[:, 0],
        original_section[:, 1],
        alpha=0.2,
        hatch="OOoo..",
        edgecolor="gray",
        facecolor="gray",
        label="Concrete",
    )

    plt.plot(
        np.append(original_section[:, 0], original_section[0, 0]),
        np.append(original_section[:, 1], original_section[0, 1]),
        color="black",
        linewidth=2,
    )

    for dia, color in zip(unique_diameters, colors, strict=True):
        mask = diameters == dia
        plt.scatter(
            original_bars[mask, 0],
            original_bars[mask, 1],
            s=dia * scaling_factor,
            color=color,
            label=f"$\\phi${int(dia * 1000)}",
        )

    plt.xlabel("")
    plt.ylabel("")
    plt.grid(False)
    all_x, all_y = original_section[:, 0], original_section[:, 1]
    plt.xticks(np.unique(all_x))
    plt.yticks(np.unique(all_y))

    ax.spines[["top", "right", "bottom", "left"]].set_visible(False)
    plt.legend()
    plt.tight_layout()
    plt.show()


@timer
def rotate_coordinates(
    coordinates: np.ndarray, angle_deg: float, pivot: np.ndarray | None = None, delta: np.ndarray | None = None
) -> np.ndarray:
    """Rotate and translate a set of coordinates in 2D plane.

    Args:
        coordinates (np.ndarray): Original coordinates.
        angle_deg (float): Angle in degrees.
        pivot (np.ndarray | None, optional): The pivot point for rotation.
        delta (np.ndarray | None, optional): Translation vector.

    Returns:
        np.ndarray: Transformed coordinates.
    """
    angle_rad = np.radians(angle_deg)
    if pivot is None:
        pivot = np.array([0, 0])
    if delta is None:
        delta = np.array([0, 0])

    matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad)], [np.sin(angle_rad), np.cos(angle_rad)]])
    rotated_coordinates = np.dot(coordinates - pivot, matrix.T) + pivot + delta
    return rotated_coordinates


if __name__ == "__main__":
    np.set_printoptions(precision=4, suppress=True)
    coordinates = np.array([[0.0, 0.0], [0.2, 0.0], [0.2, 1.0], [0.5, 1], [0.5, 1.2], [0, 1.2], [0.0, 1.0]])
    bars = np.array(
        [
            [0.05, 0.05, 0.022, 42000, 21000000],
            [0.15, 0.05, 0.022, 42000, 21000000],
            [0.05, 0.95, 0.008, 42000, 21000000],
            [0.15, 0.95, 0.008, 42000, 21000000],
            [0.10, 0.85, 0.032, 42000, 21000000],
            [0.25, 1.15, 0.032, 42000, 21000000],
            [0.05, 1.15, 0.016, 42000, 21000000],
            [0.45, 1.15, 0.016, 42000, 21000000],
        ]
    )

    rotated_coordinates = rotate_coordinates(coordinates, 180, pivot=None, delta=None)
    rotated_section = Polygon(rotated_coordinates)

    bar_coordinates = bars[:, :2]
    rotated_bar_coordinates = rotate_coordinates(bar_coordinates, 180, pivot=None, delta=None)
    rotated_reinforced_bars = np.hstack((rotated_bar_coordinates, bars[:, 2:]))

    curve_data = get_curve2d(coordinates, bars)
    plot_curve2d(curve_data, coordinates, bars)
