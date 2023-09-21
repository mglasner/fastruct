"""Utils functions for plotting module."""
import matplotlib.pyplot as plt


def close_event(event):
    """Close plot when the 'q' key is pressed."""
    if event.key == "q":
        plt.close(event.canvas.figure)
