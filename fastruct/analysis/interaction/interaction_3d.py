"""3D MP interaction curve."""
from queue import Queue

import numpy as np

from fastruct.analysis.interaction.interaction_2d import get_curve2d, rotate_coordinates


def get_curve3d(
    angle: float,
    original_coordinates: np.ndarray,
    original_reinforced_bars: np.ndarray,
    mp_design_list: list,
    progress_queue: Queue,
) -> None:
    """Process a single angle to calculate design parameters and store them in a shared list.

    Args:
        angle (float): The angle to process.
        original_coordinates (np.ndarray): The original coordinates of the concrete section.
        original_reinforced_bars (np.ndarray): The original coordinates and properties of the reinforced bars.
        mp_design_list (list): A shared list to store the calculated design parameters.
        progress_queue: A queue to track the progress of the task. A "1" is put into the queue when the task is
                        complete.

    Returns:
        None: Results are stored in the shared list mp_design_list.
    """
    coordinates = rotate_coordinates(original_coordinates, angle, pivot=None, delta=None)
    original_bars_coordinates = original_reinforced_bars[:, :2]
    bar_coordinates = rotate_coordinates(original_bars_coordinates, angle, pivot=None, delta=None)
    reinforced_bars = np.hstack((bar_coordinates, original_reinforced_bars[:, 2:]))

    mp_nominal, reduction_factors = get_curve2d(coordinates, reinforced_bars)
    mp_design = mp_nominal * reduction_factors
    m, p = mp_design[:, 0], mp_design[:, 1]

    angle_rad = np.radians(angle)
    mx = m * np.cos(angle_rad)
    my = m * np.sin(angle_rad)

    mp_design_list.append(np.array([mx, my, m, p]))
    progress_queue.put(1)
