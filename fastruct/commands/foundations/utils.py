"""Utility functions for foundations commands."""
from collections.abc import Iterable
from typing import Literal

from rich.text import Text

PERCENTAJE_0 = 0
PERCENTAJE_80 = 80
PERCENTAJE_100 = 100

MAX_STRESS_COLOR = "red"
LIMIT_STRESS_COLOR = "yellow"
MIN_PERCENTAJE_COLOR = "blue"


def data_by_method(
    stress: list[float],
    percentaje: list[float],
    method: Literal["bi-directional", "one-direction", "compare"],
    max_stress: float,
    limit_stress: float | None = None,
    no_color: bool = False,
) -> list[str | Text]:
    """Generate row data by analysis method."""
    if limit_stress is None:
        limit_stress = max_stress

    if no_color:
        max_stress_color = ""
        limit_stress_color = ""
        min_percentaje_color = ""

    else:
        max_stress_color = "red"
        limit_stress_color = "yellow"
        min_percentaje_color = "blue"

    def format_stress(s: float) -> str | Text:
        if s == max_stress:
            return Text(f"{s:.2f}", style=f"{max_stress_color} italic bold")
        elif limit_stress <= s < max_stress:
            return Text(f"{s:.2f}", style=f"{limit_stress_color} italic")
        elif s < limit_stress:
            return Text(f"{s:.2f}", style="italic")
        else:
            return f"{s:.2f}"

    def format_percentaje(p: float) -> str | Text:  # noqa: PLR0911
        if p == PERCENTAJE_0:
            return Text(f"{p:.0f}%", style=f"{min_percentaje_color} bold")
        elif p < PERCENTAJE_80:
            return Text(f"{p:.0f}%", style="bold")
        elif p <= PERCENTAJE_100:
            return Text(f"{p:.0f}%", style="")
        else:
            return f"{p:.2f}"

    data = []

    if method == "bi-direction":
        data.extend(
            [format_stress(stress) if stress is not None else "∞", format_percentaje(percentaje)]  # type: ignore
        )
    elif method == "one-direction":
        stress_x, stress_y = stress
        percentaje_x, percentaje_y = percentaje
        data.extend(
            [
                format_stress(stress_x) if stress_x is not None else "∞",
                format_percentaje(percentaje_x),
                format_stress(stress_y) if stress_y is not None else "∞",
                format_percentaje(percentaje_y),
            ]
        )
    elif method == "compare":
        bi_stress, stress_x, stress_y = stress
        bi_percentaje, percentaje_x, percentaje_y = percentaje
        data.extend(
            [
                format_stress(bi_stress) if bi_stress is not None else "∞",
                format_percentaje(bi_percentaje),
                format_stress(stress_x) if stress_x is not None else "∞",
                format_percentaje(percentaje_x),
                format_stress(stress_y) if stress_y is not None else "∞",
                format_percentaje(percentaje_y),
            ]
        )

    return data


def format_stress(stress: float, max_stress: float) -> str | Text:
    """Format to stress cell."""
    return Text(f"{stress:.2f}", style="red") if stress == max_stress else f"{stress:.2f}"


def get_max_value(data: list[float | None] | list[tuple[float | None, ...]]) -> float | None:
    """Get the maximum value from a list containing either floats, Nones, or tuples of floats and Nones.

    Args:
        data: A list containing either floats, Nones, or tuples of floats and Nones.

    Returns:
        The maximum value found or None if all values are None.
    """
    if data and isinstance(data[0], tuple):
        flat_data = [
            value
            for sublist in data
            if sublist is not None
            for value in (sublist if isinstance(sublist, Iterable) else [])
            if value is not None
        ]
    else:
        flat_data = [value for value in data if value is not None]

    return max(flat_data, default=None)  # type: ignore
