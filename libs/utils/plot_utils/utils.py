""" plotting utils """
import os

from libs.utils.constants import STANDARD_COLORS

WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]


def plot_xaxis_disperse(axis_obj, every_nth: int = 2, dynamic: bool = True):
    """Plot Xaxis Disperse

    Arguments:
        axis_obj {} -- Matplotlib axis object, likely a dictionary

    Keyword Arguments:
        every_nth {int} -- tick mark interval (default: {2})
        dynamic {bool} -- determines if ticks should end on even or odd (default: {True})
    """
    num_ticks = len(axis_obj.xaxis.get_ticklabels())
    tick_even = True
    if dynamic:
        tick_even = not bool(num_ticks % 2)

    for n_val, label in enumerate(axis_obj.xaxis.get_ticklabels()):
        if tick_even:
            if n_val % every_nth == 0:
                label.set_visible(False)
        else:
            if n_val % every_nth != 0:
                label.set_visible(False)


def is_data_list(data) -> bool:
    """ Determines if data provided is a list [of lists] or simply a vector of data """
    for dat in data:
        if isinstance(dat, list):
            return True
    return False


def save_or_render_plot(plot_object, fig, save_fig: bool, title: str, filename: str,
                        plot_type: str) -> None:
    """try to save or render the plot

    Args:
        plot_object (_type_): "plt" in matplotlib
        fig (_type_): matplotlib fig
        save_fig (bool): to save or not to save
        title (str): title of plt
        filename (str): filename to save
    """
    # pylint: disable=too-many-arguments
    try:
        if save_fig:
            temp_path = os.path.join("output", "temp")
            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plot_object.close(fig)
                plot_object.clf()
                return

            filename = os.path.join(temp_path, filename)
            if os.path.exists(filename):
                os.remove(filename)

            plot_object.savefig(filename)

        else:
            plot_object.show()

    except: # pylint: disable=bare-except
        print(
            f"{WARNING}Warning: plot failed to render in '{plot_type}' of title: " +
            f"{title}{NORMAL}")
