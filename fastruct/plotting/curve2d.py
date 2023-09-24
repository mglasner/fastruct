"""Interactive M-P 2d curve."""
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

from fastruct.common.decorators import timer


@timer
def plot_curve2d(curve_data: np.ndarray, section: np.ndarray, bars: np.ndarray) -> None:
    """Plot the 2D interaction axial force vs. bending moment curve, along with the original section.

    Args:
        curve_data (np.ndarray): An array containing pairs of (M, P) for the curve.
        section (np.ndarray): Coordinates of the original section.
        bars (np.ndarray): Coordinates and properties of reinforcing bars in the original section.

    Returns:
        None
    """
    plt.close("all")
    m, p = curve_data[:, 0], curve_data[:, 1]

    fig = plt.figure(figsize=(15, 6))
    fig.suptitle("Interaction M-P 2D curve")
    fig.text(
        0.5,  # x coordinate, 0 leftmost positioned, 1 rightmost
        0.01,  # y coordinate, 0 bottommost positioned, 1 topmost
        "Press 'q' to close the figure.",
        ha="center",
        fontsize=10,
        color="grey",
    )
    ax = plt.subplot(1, 2, 1, aspect="equal")
    plot_concrete_section(ax, section, bars)

    plt.subplot(1, 2, 2)
    plt.plot(m, p, label="M-P Curve", linewidth=2)
    plt.fill_between(m, p, color="skyblue", alpha=0.4)

    plt.axhline(0, color="black", linestyle="--", linewidth=2, label="P=0")
    plt.axvline(0, color="black", linestyle="--", linewidth=2, label="M=0")

    max_p, min_p = np.max(p), np.min(p)
    max_m, min_m = np.max(m), np.min(m)

    max_p_m_values = m[p == max_p]
    closest_to_zero_m = max_p_m_values[np.argmin(np.abs(max_p_m_values))]
    plt.scatter([closest_to_zero_m], [max_p], color="red", zorder=5)
    plt.annotate(
        f"({round(closest_to_zero_m)}, {round(max_p)})",
        (closest_to_zero_m, max_p),
        textcoords="offset points",
        xytext=(10, 10),
        ha="center",
    )

    min_p_m_values = m[p == min_p]
    plt.scatter(min_p_m_values, [min_p] * len(min_p_m_values), color="blue", zorder=5)
    plt.annotate(
        f"({round(min_p_m_values[0])}, {round(min_p)})",
        (min_p_m_values[0], min_p),
        textcoords="offset points",
        xytext=(10, -10),
        ha="center",
    )

    plt.scatter([max_m, min_m], [p[m == max_m][0], p[m == min_m][0]], color="green", zorder=5)
    plt.annotate(
        f"({round(max_m)}, {round(p[m == max_m][0])})",
        (max_m, p[m == max_m][0]),
        textcoords="offset points",
        xytext=(20, 10),
        ha="center",
    )
    plt.annotate(
        f"({round(min_m)}, {round(p[m == min_m][0])})",
        (min_m, p[m == min_m][0]),
        textcoords="offset points",
        xytext=(-20, 10),
        ha="center",
    )

    zero_p_m_values = m[np.isclose(p, 0, atol=1e-1)]
    plt.scatter(zero_p_m_values, [0] * len(zero_p_m_values), color="orange", zorder=5)
    for moment in zero_p_m_values:
        plt.annotate(f"({round(moment)}, 0)", (moment, 0), textcoords="offset points", xytext=(0, 10), ha="center")

    plt.xlabel("Bending Moment (M)")
    plt.ylabel("Axial Force (P)")
    plt.grid(True)
    plt.legend()

    plt.grid(False)
    all_x, all_y = section[:, 0], section[:, 1]
    plt.xticks(np.unique(all_x))
    plt.yticks(np.unique(all_y))

    plt.tight_layout(rect=[0, 0, 0.85, 1])

    plt.show()


def sort_points_counter_clockwise(points: np.ndarray) -> np.ndarray:
    """Sort points in counter-clockwise order."""
    centroid = np.mean(points, axis=0)
    angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
    sort_order = np.argsort(angles)
    return points[sort_order]


def update_ax3(
    event: Any,
    mp_design_list: list[np.ndarray],
    ax2: plt.Axes,
    ax3: plt.Axes,
    slice_values: np.ndarray,
    slice_idx: list[int],
    xlim: tuple[float, float],
    ylim: tuple[float, float],
) -> None:
    """Callback function to update ax3 plot with new slices based on P value.

    Parameters:
        event: Event from the Matplotlib button.
        mp_design_list: List of interaction curves data.
        ax2: 3D Axes object for plotting.
        ax3: 2D Axes object for plotting.
        slice_values: Array of P values for slicing.
        slice_idx: Mutable list for slice index.
        xlim: X-axis limits for 2D plot.
        ylim: Y-axis limits for 2D plot.
    """
    ax3.clear()
    ax3.set_xlim(xlim)
    ax3.set_ylim(ylim)

    # Clear previous surfaces in the 3D plot
    for collection in ax2.collections:
        collection.remove()

    slice_value = slice_values[slice_idx[0]]
    points_to_plot = []

    for mp_data in mp_design_list:
        idx = np.where(np.isclose(mp_data[2], slice_value, atol=1))[0]
        if len(idx) > 0:
            points_to_plot.extend(list(zip(mp_data[0][idx], mp_data[1][idx], strict=True)))

    if points_to_plot:
        points_to_plot = np.array(points_to_plot)
        sorted_points = sort_points_counter_clockwise(points_to_plot)
        closed_points = np.vstack([sorted_points, sorted_points[0, :]])
        ax3.plot(closed_points[:, 0], closed_points[:, 1], "b-")
        ax3.fill(closed_points[:, 0], closed_points[:, 1], color="r", alpha=0.4)

    # Add the surface to the 3D plot
    x_range = np.linspace(xlim[0], xlim[1], 2)
    y_range = np.linspace(ylim[0], ylim[1], 2)
    x_surface, y_surface = np.meshgrid(x_range, y_range)
    z_surface = np.full(x_surface.shape, slice_value)
    ax2.plot_surface(x_surface, y_surface, z_surface, color="r", alpha=0.4)

    ax3.set_title(f"Horizontal Slice at P = {slice_value:.1f}")  # Adding the value of P to the title
    ax3.set_xlabel("Mx")
    ax3.set_ylabel("My")
    plt.draw()

    slice_idx[0] = (slice_idx[0] + 1) % len(slice_values)


def plot_curve3d(mp_design_list: list[np.ndarray], coordinates: np.ndarray, reinforced_bars: np.ndarray) -> None:
    """Plot the 3D interaction curves and original concrete section."""
    plt.close("all")
    fig = plt.figure(figsize=(15, 6))
    fig.suptitle("Interaction M-P 3D curve")
    fig.text(0.5, 0.01, "Press 'q' to close the figure.", ha="center", fontsize=10, color="grey")

    # Plot the concrete section
    ax1 = plt.subplot(1, 3, 1, aspect="equal")
    plot_concrete_section(ax1, coordinates, reinforced_bars)

    # Plot the 3D curves
    ax2 = fig.add_subplot(132, projection="3d")
    for mp_data in mp_design_list:
        ax2.plot(mp_data[0], mp_data[1], mp_data[2], color="b", linewidth=1, alpha=0.25)

    ax2.view_init(elev=5, azim=45)
    ax2.set_xlabel("Mx")
    ax2.set_ylabel("My")
    ax2.set_zlabel("P")

    all_mx = np.concatenate([mp_data[0] for mp_data in mp_design_list])
    all_my = np.concatenate([mp_data[1] for mp_data in mp_design_list])
    xlim = (1.1 * np.min(all_mx), 1.1 * np.max(all_mx))
    ylim = (1.1 * np.min(all_my), 1.1 * np.max(all_my))

    all_p = np.concatenate([mp_data[2] for mp_data in mp_design_list])
    slice_values = np.linspace(np.min(all_p), 0.95 * np.max(all_p), 5)
    slice_idx = [0]  # Mutable for callback

    ax3 = fig.add_subplot(133, aspect="equal")
    ax3.set_xlim(xlim)
    ax3.set_ylim(ylim)
    update_ax3(None, mp_design_list, ax2, ax3, slice_values, slice_idx, xlim, ylim)

    ax_button = plt.axes([0.25, 0.02, 0.1, 0.05])
    button = Button(ax_button, "Next Slice")
    button.on_clicked(lambda event: update_ax3(event, mp_design_list, ax2, ax3, slice_values, slice_idx, xlim, ylim))

    plt.show()


def plot_concrete_section(ax, coordinates: np.ndarray, bars: np.ndarray, scaling_factor: int = 2000) -> None:
    """Utility function to plot the concrete section and reinforcement bars.

    Args:
        ax (matplotlib.Axes): The matplotlib Axes object to plot on.
        coordinates (np.ndarray): The x, y coordinates of the concrete section.
        bars (np.ndarray): The x, y coordinates and properties of the reinforcement bars.
        scaling_factor (int, optional): Scaling factor for the reinforcement bars. Defaults to 2000.

    Returns:
        None
    """
    unique_diameters = np.unique(bars[:, 2])
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_diameters)))

    ax.spines[["top", "right", "bottom", "left"]].set_visible(False)

    ax.fill(
        coordinates[:, 0],
        coordinates[:, 1],
        alpha=0.2,
        hatch="OOoo..",
        edgecolor="gray",
        facecolor="gray",
        label="Concrete",
    )
    ax.plot(
        np.append(coordinates[:, 0], coordinates[0, 0]),
        np.append(coordinates[:, 1], coordinates[0, 1]),
        color="black",
        linewidth=2,
    )

    for dia, color in zip(unique_diameters, colors, strict=True):
        mask = bars[:, 2] == dia
        ax.scatter(
            bars[mask, 0],
            bars[mask, 1],
            s=dia * scaling_factor,
            color=color,
            label=f"$\\phi${int(dia * 1000)}",
        )

    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
