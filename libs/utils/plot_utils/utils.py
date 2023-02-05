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
