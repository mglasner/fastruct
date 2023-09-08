"""Utility functions for foundations commands."""
from collections.abc import Iterable
from typing import Literal

import typer

from fastruct.analysis.foundations.bi_direction import bi_direction_analysis
from fastruct.analysis.foundations.one_direction import one_direction_analysis
from fastruct.models.foundation import Foundation


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


def stresses_and_percentajes_by_method(
    foundation: Foundation, method: Literal["bi-directional", "one-direction", "compare"]
) -> tuple[
    list[float | None]
    | list[tuple[float | None, float | None]]
    | list[tuple[float | None, float | None, float | None]],
    list[float] | list[tuple[float, float]] | list[tuple[float, float, float]],
]:
    """Utility funtion for getting stresses and percentajes by method."""
    bi_stresses, bi_percentajes = bi_direction_analysis(foundation)
    one_stresses, one_percentajes = one_direction_analysis(foundation)
    all_stresses = [(s1, s2, s3) for s1, (s2, s3) in zip(bi_stresses, one_stresses, strict=True)]
    all_percentajes = [(p1, p2, p3) for p1, (p2, p3) in zip(bi_percentajes, one_percentajes, strict=True)]

    if method == "bi-direction":
        stresses, percentajes = bi_stresses, bi_percentajes

    elif method == "one-direction":
        stresses, percentajes = one_stresses, one_percentajes

    elif method == "compare":
        stresses, percentajes = all_stresses, all_percentajes
    else:
        print(f"Unkwnown method: {method}")
        raise typer.Exit()

    return stresses, percentajes
