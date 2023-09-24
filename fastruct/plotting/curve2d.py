"""Interactive M-P 2d curve."""
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import Button
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from mpl_toolkits.mplot3d.art3d import Line3D


def plot_2d(ax: plt.Axes, curve_data: np.ndarray) -> None:
    """Plot the main 2D curve on the given Axes object."""
    m, p = curve_data[:, 0], curve_data[:, 1]
    ax.plot(m, p, label="M-P Curve", linewidth=2)
    ax.fill_between(m, p, color="skyblue", alpha=0.4)
    ax.axhline(0, color="black", linestyle="--", linewidth=2, label="P=0")
    ax.axvline(0, color="black", linestyle="--", linewidth=2, label="M=0")
    ax.set_xlabel("Bending Moment (M)")
    ax.set_ylabel("Axial Force (P)")
    ax.grid(True)


def annotate_2d_curve(ax: plt.Axes, curve_data: np.ndarray) -> None:
    """Add annotations to the 2D curve on the given Axes object."""
    m, p = curve_data[:, 0], curve_data[:, 1]
    max_p, min_p = np.max(p), np.min(p)
    max_m, min_m = np.max(m), np.min(m)

    # Annotate points where P is maximum
    max_p_m_values = m[p == max_p]
    closest_to_zero_m = max_p_m_values[np.argmin(np.abs(max_p_m_values))]
    ax.scatter([closest_to_zero_m], [max_p], color="red", zorder=5)
    ax.annotate(
        f"({round(closest_to_zero_m)}, {round(max_p)})",
        (closest_to_zero_m, max_p),
        textcoords="offset points",
        xytext=(10, 10),
        ha="center",
    )

    # Annotate points where P is minimum
    min_p_m_values = m[p == min_p]
    ax.scatter(min_p_m_values, [min_p] * len(min_p_m_values), color="blue", zorder=5)
    ax.annotate(
        f"({round(min_p_m_values[0])}, {round(min_p)})",
        (min_p_m_values[0], min_p),
        textcoords="offset points",
        xytext=(10, -10),
        ha="center",
    )
    ax.scatter([max_m, min_m], [p[m == max_m][0], p[m == min_m][0]], color="green", zorder=5)
    ax.annotate(
        f"({round(max_m)}, {round(p[m == max_m][0])})",
        (max_m, p[m == max_m][0]),
        textcoords="offset points",
        xytext=(20, 10),
        ha="center",
    )
    ax.annotate(
        f"({round(min_m)}, {round(p[m == min_m][0])})",
        (min_m, p[m == min_m][0]),
        textcoords="offset points",
        xytext=(-20, 10),
        ha="center",
    )

    zero_p_m_values = m[np.isclose(p, 0, atol=0.5)]
    if len(zero_p_m_values) > 0:
        min_zero_m = np.min(zero_p_m_values)
        max_zero_m = np.max(zero_p_m_values)
        ax.scatter([min_zero_m, max_zero_m], [0, 0], color="orange", zorder=5)
        ax.annotate(
            f"({round(min_zero_m)}, 0)", (min_zero_m, 0), textcoords="offset points", xytext=(0, 10), ha="center"
        )
        ax.annotate(
            f"({round(max_zero_m)}, 0)", (max_zero_m, 0), textcoords="offset points", xytext=(0, 10), ha="center"
        )


def plot_curve2d(curve_data: np.ndarray, section: np.ndarray, bars: np.ndarray) -> None:
    """Plot the standalone 2D curve along with the original concrete section."""
    plt.close("all")
    fig = plt.figure(figsize=(15, 6))

    ax_section = plt.subplot(1, 2, 1, aspect="equal")
    # Assuming plot_concrete_section is a function you already have
    plot_concrete_section(ax_section, section, bars)

    ax_curve = plt.subplot(1, 2, 2)
    plot_2d(ax_curve, curve_data)
    annotate_2d_curve(ax_curve, curve_data)

    plt.show()


def plot_curve3d(
    mp_design_list: list[np.ndarray], angles, coordinates: np.ndarray, reinforced_bars: np.ndarray
) -> None:
    """Plot the 3D interaction curves and original concrete section."""
    plt.close("all")
    fig = plt.figure(figsize=(15, 9))  # Increase the figure size for better layout
    fig.suptitle("Interaction M-P 3D curve")
    fig.text(0.5, 0.01, "Press 'q' to close the figure.", ha="center", fontsize=10, color="grey")

    gs = GridSpec(2, 3, height_ratios=[1, 1])  # 2 rows, 3 columns

    # Plot the concrete section
    ax1 = plt.subplot(gs[0:2, 0], aspect="equal")  # Spans both rows
    plot_concrete_section(ax1, coordinates, reinforced_bars)

    # Plot the 3D curves
    ax2 = plt.subplot(gs[0:2, 1], projection="3d")  # Spans both rows
    plot_3d_curve(ax2, mp_design_list)
    set_3d_aspect_equal(ax2)

    # Plot 2D curve (new subplot)
    ax3 = plt.subplot(gs[0, 2])  # Top right
    angle_idx = [0]
    plot_2d_curve(None, mp_design_list, ax3, ax2, angles, angle_idx)

    ax_button2 = inset_axes(ax3, width="10%", height="10%", loc="lower right")
    button2 = Button(ax_button2, "↺")
    button2.on_clicked(lambda event: plot_2d_curve(event, mp_design_list, ax3, ax2, angles, angle_idx))

    # Plot horizontal slice Mx vs My
    ax4 = plt.subplot(gs[1, 2], aspect="equal")  # Bottom right
    slice_values = np.linspace(np.min(mp_design_list[0][3]), 0.99 * np.max(mp_design_list[0][3]), 12)
    slice_idx = [6]  # Mutable for callback
    plot_horizontal_slice(None, mp_design_list, ax2, ax4, slice_values, slice_idx)

    ax_button = inset_axes(ax4, width="10%", height="10%", loc="lower right")
    button = Button(ax_button, "↑")
    button.on_clicked(lambda event: plot_horizontal_slice(event, mp_design_list, ax2, ax4, slice_values, slice_idx))

    plt.show()


def plot_2d_curve(
    event: Any, mp_design_list: list[np.ndarray], ax3: plt.Axes, ax2: plt.Axes, angles: np.ndarray, angle_idx: list[int]
) -> None:
    """Update 2D curve plot and highlight the corresponding curve in 3D plot based on the angle.

    Parameters:
        event: Event from the Matplotlib button.
        mp_design_list: List of interaction curves data.
        ax3: 2D Axes object for plotting.
        ax2: 3D Axes object for plotting.
        angles: Array of angle values.
        angle_idx: Mutable list for angle index.
    """
    ax3.clear()

    # Remove the previously highlighted line in 3D plot if any
    if hasattr(ax2, "highlighted_line"):
        ax2.highlighted_line.remove()
        del ax2.highlighted_line

    current_angle = angles[angle_idx[0]]
    current_mp_data = mp_design_list[angle_idx[0]]
    m, p = current_mp_data[2], current_mp_data[3]
    mp_2d_data = np.column_stack((m, p))

    # Your plot_2d and annotate_2d_curve functions are assumed to be defined elsewhere
    plot_2d(ax3, mp_2d_data)
    annotate_2d_curve(ax3, mp_2d_data)

    ax3.set_title(f"2D Curve at {current_angle:.1f}°\n")  # Adding the angle to the title
    ax3.set_xlabel("Bending Moment (M)")
    ax3.set_ylabel("Axial Force (P)")

    # Highlight the corresponding curve in 3D plot
    x, y, z = current_mp_data[0], current_mp_data[1], current_mp_data[3]
    ax2.highlighted_line = Line3D(x, y, z, color="b", linewidth=2, alpha=0.4)
    ax2.add_artist(ax2.highlighted_line)

    plt.draw()

    # Increment the angle index by 8 for next button press, loop back to 0 if exceeded
    angle_idx[0] = (angle_idx[0] + 8) % len(angles)


def plot_3d_curve(ax2, mp_design_list: list[np.ndarray]) -> None:
    """Plot the 3D interaction curves on the given Axes3D object."""
    # Plot the 3D curves
    for mp_data in mp_design_list:
        ax2.plot(mp_data[0], mp_data[1], mp_data[3], color="g", linewidth=1, alpha=0.4)

    ax2.view_init(elev=20, azim=45)
    ax2.set_xlabel("Mx")
    ax2.set_ylabel("My")
    ax2.set_zlabel("P")


def sort_points_counter_clockwise(points: np.ndarray) -> np.ndarray:
    """Sort points in counter-clockwise order."""
    centroid = np.mean(points, axis=0)
    angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
    sort_order = np.argsort(angles)
    return points[sort_order]


def plot_horizontal_slice(
    event: Any,
    mp_design_list: list[np.ndarray],
    ax2: plt.Axes,
    ax4: plt.Axes,
    slice_values: np.ndarray,
    slice_idx: list[int],
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
    ax4.clear()
    all_mx = np.concatenate([mp_data[0] for mp_data in mp_design_list])
    all_my = np.concatenate([mp_data[1] for mp_data in mp_design_list])
    xlim = (1.1 * np.min(all_mx), 1.1 * np.max(all_mx))
    ylim = (1.1 * np.min(all_my), 1.1 * np.max(all_my))
    ax4.set_xlim(xlim)
    ax4.set_ylim(ylim)

    # Clear previous surfaces in the 3D plot
    for collection in ax2.collections:
        collection.remove()

    slice_value = slice_values[slice_idx[0]]
    points_to_plot = []

    for mp_data in mp_design_list:
        idx = np.where(np.isclose(mp_data[3], slice_value, atol=1))[0]
        if len(idx) > 0:
            points_to_plot.extend(list(zip(mp_data[0][idx], mp_data[1][idx], strict=True)))

    if points_to_plot:
        points_to_plot = np.array(points_to_plot)
        sorted_points = sort_points_counter_clockwise(points_to_plot)
        closed_points = np.vstack([sorted_points, sorted_points[0, :]])
        ax4.plot(closed_points[:, 0], closed_points[:, 1], "g")
        ax4.fill(closed_points[:, 0], closed_points[:, 1], color="r", alpha=0.4)

    # Add the surface to the 3D plot
    x_range = np.linspace(xlim[0], xlim[1], 2)
    y_range = np.linspace(ylim[0], ylim[1], 2)
    x_surface, y_surface = np.meshgrid(x_range, y_range)
    z_surface = np.full(x_surface.shape, slice_value)
    ax2.plot_surface(x_surface, y_surface, z_surface, color="r", alpha=0.4)

    ax4.set_title(f"Horizontal Slice at P = {slice_value:.1f}")  # Adding the value of P to the title
    ax4.set_xlabel("Bending Moment (Mx)")
    ax4.set_ylabel("Bending Moment (My)")

    ax4.axhline(0, color="black", linestyle="--", linewidth=2, label="Mx=0")
    ax4.axvline(0, color="black", linestyle="--", linewidth=2, label="My=0")
    ax4.grid(True)

    plt.draw()

    slice_idx[0] = (slice_idx[0] + 1) % len(slice_values)


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


def set_3d_aspect_equal(ax: plt.Axes):
    """Set aspect ratio to be equal in a 3D plot."""
    # Retrieve axis limits
    xlim = ax.get_xlim3d()
    ylim = ax.get_ylim3d()
    zlim = ax.get_zlim3d()

    # Calculate ranges for x, y, z
    x_range = np.abs(xlim[1] - xlim[0])
    y_range = np.abs(ylim[1] - ylim[0])
    z_range = np.abs(zlim[1] - zlim[0])

    # Find the maximum range value
    max_range = np.max([x_range, y_range, z_range])

    # Calculate bounds for setting aspect ratio
    ax.set_xlim3d([np.mean(xlim) - max_range / 4.0, np.mean(xlim) + max_range / 4.0])
    ax.set_ylim3d([np.mean(ylim) - max_range / 4.0, np.mean(ylim) + max_range / 4.0])
    ax.set_zlim3d([np.mean(zlim) - max_range / 2.0, np.mean(zlim) + max_range / 2.0])
