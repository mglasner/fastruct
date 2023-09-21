"""Interactive M-P 2d curve."""

import matplotlib.pyplot as plt
import numpy as np

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
    diameters = bars[:, 2]
    scaling_factor = 2000

    unique_diameters = np.unique(diameters)
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_diameters)))

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

    ax = plt.subplot(1, 2, 1, aspect="equal")
    plt.fill(
        section[:, 0],
        section[:, 1],
        alpha=0.2,
        hatch="OOoo..",
        edgecolor="gray",
        facecolor="gray",
        label="Concrete",
    )

    plt.plot(
        np.append(section[:, 0], section[0, 0]),
        np.append(section[:, 1], section[0, 1]),
        color="black",
        linewidth=2,
    )

    for dia, color in zip(unique_diameters, colors, strict=True):
        mask = diameters == dia
        plt.scatter(
            bars[mask, 0],
            bars[mask, 1],
            s=dia * scaling_factor,
            color=color,
            label=f"$\\phi${int(dia * 1000)}",
        )

    plt.grid(False)
    all_x, all_y = section[:, 0], section[:, 1]
    plt.xticks(np.unique(all_x))
    plt.yticks(np.unique(all_y))

    ax.spines[["top", "right", "bottom", "left"]].set_visible(False)

    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.tight_layout(rect=[0, 0, 0.85, 1])

    plt.show()
