"""Foundation drawings module."""
import matplotlib.pyplot as plt
import numpy as np

from fastruct.models.foundation import Foundation


def draw_foundation(foundation: Foundation):
    """Draw 3D foundation."""
    lx, ly, lz = foundation.lx, foundation.ly, foundation.lz
    plt.close("all")
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title(foundation)

    ax.set_box_aspect([lx, ly, lz])

    x = np.linspace(0, lx, 2)
    y = np.linspace(0, ly, 2)
    z = np.linspace(0, lz, 2)

    # Bottom and top surfaces
    add_surface(ax, x, y, 0)
    add_surface(ax, x, y, lz)

    # Front and back surfaces
    add_surface(ax, x, z, 0, plane_orientation="xz")
    add_surface(ax, x, z, ly, plane_orientation="xz")

    # Left and right surfaces
    add_surface(ax, y, z, 0, plane_orientation="yz")
    add_surface(ax, y, z, lx, plane_orientation="yz")

    # Adding the force arrow at position (ex, ey) pointing downwards
    ex, ey = foundation.ex, foundation.ey
    greater_side = max(lx, ly, lz)
    ax.quiver(
        lx / 2 + ex,
        ly / 2 + ey,
        greater_side / 2 + lz,
        0,
        0,
        -greater_side / 2,
        color="red",
        arrow_length_ratio=0.2,
        linewidth=2.5,
        zorder=100,
    )

    ax.axis("off")
    plt.show()


def add_surface(axis, x: np.ndarray, y: np.ndarray, z_value: float, plane_orientation: str = "xy"):
    """Adds a surface to the given axis.

    Args:
        axis: The 3D axis to add the surface to.
        x (np.ndarray): X coordinates for the meshgrid.
        y (np.ndarray): Y coordinates for the meshgrid.
        z_value (float): The constant Z value for the surface.
        plane_orientation (str): Which plane the surface should lie on ('xy', 'yz', 'xz').
    """
    x, y = np.meshgrid(x, y)
    z = np.full(x.shape, z_value)
    surface_color = "#444654"
    edge_color = "#343541"

    if plane_orientation == "yz":
        axis.plot_surface(z, x, y, alpha=0.5, facecolor=surface_color, edgecolor=edge_color, zorder=1)
    elif plane_orientation == "xz":
        axis.plot_surface(x, z, y, alpha=0.5, facecolor=surface_color, edgecolor=edge_color, zorder=1)
    else:
        axis.plot_surface(x, y, z, alpha=0.5, facecolor=surface_color, edgecolor=edge_color, zorder=1)
