"""Foundations bi direction analysis."""
from collections import OrderedDict
from math import sqrt

from models.foundation import Foundation
from models.load import Load
from shapely.geometry import LineString, Polygon


def bi_direction_analysis(foundation: Foundation) -> tuple[list[float | None], list[float]]:
    """Returns maximun stresses and support percentaje by directions x and y."""
    results = [get_bi_directional_percentaje_and_stress(foundation, load) for load in foundation.loads]
    stresses = [stress for stress, _ in results]
    percentajes = [percentaje for _, percentaje in results]

    return stresses, percentajes


def calculate_bi_directional_stress(
    axial: float, moment_x: float, moment_y: float, lx: float, ly: float
) -> float | None:
    """Calculate stress over foundation for given forces and geometry."""
    area = lx * ly
    inertia_x = lx**3 * ly / 12
    inertia_y = ly**3 * lx / 12
    return axial / area + abs(moment_x) * ly / 2 / inertia_x + abs(moment_y) * lx / 2 / inertia_y


def get_bi_directional_percentaje_and_stress(foundation: Foundation, load: Load) -> tuple[float | None, float]:
    """Lifting percentaje on the foundation due to combined axial and moment forces in both orthogonal directions."""
    neutral_axis = get_neutral_axis(foundation, load)
    foundation_polygon = get_foundation_xy_polygon(foundation.lx, foundation.ly)
    ex, ey = compute_excentrycity(load.p, load.mx, load.my)

    if neutral_axis is None:
        return calculate_bi_directional_stress(load.p, load.mx, load.my, foundation.lx, foundation.ly), 100

    if abs(ex) >= foundation.lx / 2 or abs(ey) >= foundation.ly / 2:
        return None, 0

    elif abs(ex) <= foundation.lx / 6 and abs(ey) <= foundation.ly / 6:
        return calculate_bi_directional_stress(load.p, load.mx, load.my, foundation.lx, foundation.ly), 100

    if not neutral_axis.intersects(foundation_polygon):
        raise ValueError("neutral axis does not intersect poligon")

    polygons = foundation_polygon.difference(neutral_axis.intersection(foundation_polygon).buffer(1e-9))
    polygon_in_compresion = None
    for polygon in polygons.geoms:
        rounded_coords = round_coordinates(list(polygon.exterior.coords))
        unique_coords = remove_duplicates(rounded_coords)
        new_polygon = Polygon(unique_coords)
        if is_in_compresion(foundation, load, new_polygon):
            polygon_in_compresion = new_polygon

    if polygon_in_compresion is None:
        raise ValueError("The is no compressed area")

    if ex == 0:
        estimated_lx = foundation.lx
    elif ey == 0:
        estimated_lx = foundation.lx / 2 + abs(neutral_axis.xy[0][0])
    else:
        estimated_lx = min(sqrt(abs(polygon_in_compresion.area * ey / ex)), foundation.lx)

    estimated_ly = polygon_in_compresion.area / estimated_lx

    if estimated_ly > foundation.ly:
        estimated_ly = foundation.ly
        estimated_lx = polygon_in_compresion.area / estimated_ly

    return (
        calculate_bi_directional_stress(load.p, load.mx, load.my, estimated_lx, estimated_ly),
        100 * polygon_in_compresion.area / foundation_polygon.area,
    )


def is_in_compresion(foundation: Foundation, load: Load, polygon: Polygon) -> bool:
    """Determine if the foundation is entirely under compressive stress.

    This function evaluates the stress state over the exterior points of a polygon
    representing a foundation under a given load. The function returns True if the
    foundation is entirely under compressive stress, False otherwise.

    Parameters:
        foundation (Foundation): The foundation object, containing geometrical properties
                                 such as dimensions.
        load (Load): The load object containing the axial and moment forces applied to
                     the foundation.
        polygon (Polygon): The Polygon object representing the XY plane section of the
                           foundation.

    Returns:
        bool: True if the entire foundation is under compressive stress, False otherwise.

    Notes:
        - The formula for stress calculation incorporates both the rectangular geometry
          of the foundation and the axial and moment forces from the load.
        - The centroid of the foundation is assumed to be at the origin (0, 0).
    """
    rx, ry = foundation.ly / sqrt(12), foundation.lx / sqrt(12)
    ex, ey = compute_excentrycity(load.p, load.mx, load.my)
    stresses = [1 + ey * y / rx**2 + ex * x / ry**2 for x, y in polygon.exterior.coords]

    # Get the stress value with the largest absolute value
    max_stress = max(stresses, key=abs)

    return max_stress >= 0


def get_foundation_xy_polygon(width: float, height: float) -> Polygon:
    """Generate a Polygon object representing a foundation in the XY plane.

    This function creates a Polygon object based on the width and height
    parameters provided. The origin of the coordinate system is considered to be
    the geometric centroid of the foundation. Therefore, the foundation extends
    from `-width/2` to `width/2` along the X-axis and from `-height/2` to
    `height/2` along the Y-axis.

    Parameters:
        width (float): The width of the foundation along the X-axis.
        height (float): The height of the foundation along the Y-axis.

    Returns:
        Polygon: A Polygon object with the four corner coordinates of the foundation.

    Notes:
        - The function assumes that the foundation is rectangular.
        - The foundation's centroid is at the origin (0, 0).
    """
    coordinates = (
        (-width / 2, -height / 2),
        (width / 2, -height / 2),
        (width / 2, height / 2),
        (-width / 2, height / 2),
    )
    return Polygon(coordinates)


def get_neutral_axis(foundation: Foundation, load: Load) -> LineString | None:
    """Calculate the neutral axis of the foundation under a given load.

    The function computes the equation of the neutral axis based on the
    foundation's dimensions and the applied load. The neutral axis is
    returned as a LineString object representing a line segment.

    Parameters:
        foundation (Foundation): The foundation object containing its dimensions.
        load (Load): The applied load object containing force and moment values.

    Returns:
        LineString: The coordinates of the two endpoints of the neutral axis.

    Notes:
        - The foundation's dimensions (lx, ly) and the applied loads (mx, my, p) are used
          in the calculations.
        - The equation of the line is derived based on the neutral axis formula considering
          bending moments and axial force.
    """
    rx, ry = foundation.ly / sqrt(12), foundation.lx / sqrt(12)
    ex, ey = compute_excentrycity(load.p, load.mx, load.my)

    if ex == 0 and ey == 0:
        return None

    if ey == 0:
        x = -1 * ry**2 / ex
        y1 = -1 * foundation.ly / 2
        y2 = foundation.ly / 2
        point1 = (x, y1)
        point2 = (x, y2)

    else:
        m = -1 * (ex * rx**2) / (ey * ry**2)
        n = -1 * rx**2 / ey
        x1 = -1 * foundation.lx / 2
        x2 = foundation.lx / 2
        point1 = (x1, m * x1 + n)
        point2 = (x2, m * x2 + n)

    neutral_axis_coords = (point1, point2)
    return LineString(neutral_axis_coords)


def compute_excentrycity(axial: float, moment_x: float, moment_y: float) -> tuple[float, float]:
    ex = moment_y / axial
    ey = -1 * moment_x / axial if moment_x >= 0 else moment_x / axial
    return ex, ey


def round_coordinates(coords: list[tuple[float, float]], decimals: int = 6) -> list[tuple[float, float]]:
    """Round the coordinates to a certain number of decimal places.

    Args:
        coords (list[tuple[float, float]]): List of coordinates to round.
        decimals (int, optional): Number of decimal places to round to. Defaults to 6.

    Returns:
        list[tuple[float, float]]: List of rounded coordinates.
    """
    return [(round(x, decimals), round(y, decimals)) for x, y in coords]


def remove_duplicates(coords: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Remove duplicate coordinates from a list.

    Args:
        coords (list[tuple[float, float]]): List of coordinates.

    Returns:
        list[tuple[float, float]]: List of unique coordinates.
    """
    return list(OrderedDict.fromkeys(coords))
