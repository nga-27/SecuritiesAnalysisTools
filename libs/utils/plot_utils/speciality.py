""" specialty """
import os

from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt

from libs.utils import dates_extractor_list

from .utils import plot_xaxis_disperse, WARNING, NORMAL


def specialty_plotting(list_of_plots: list, **kwargs):
    """Specialty Plotting

    Plot various datasets against others (different y-axes). Similar to dual plotting, in a sense.

    Arguments:
        list_of_plots {list} -- list of y-value datasets to be plotted (multiple)

    Optional Args:
        x {list} -- x-value data (default: {[]}) (length of lists)
        alt_ax_index {list} -- list of other y-value datasets to be plotted on other axis
                                (default: {[]})
        title {str} -- title of plot (default: {''})
        legend {list} -- list of plot labels in legend (default: {[]})
        save_fig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_specialty_plot.png'})

    Returns:
        None
    """
    register_matplotlib_converters()

    x_list = kwargs.get('x', [])
    alt_ax_index = kwargs.get('alt_ax_index', [])
    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    save_fig = kwargs.get('save_fig', False)
    filename = kwargs.get('filename', 'temp_specialty_plot.png')

    if len(x_list) < 1:
        x_list = dates_extractor_list(list_of_plots[0])
    fig, axis = plt.subplots()

    for i, plot_item in enumerate(list_of_plots):
        if i not in alt_ax_index:
            axis.plot(x_list, plot_item)

    ax2 = axis.twinx()
    for i, plot_item in enumerate(list_of_plots):
        if i in alt_ax_index:
            ax2.plot(x_list, plot_item, color='tab:purple')

    plt.title(title)
    ax2.set_ylabel(legend[0])
    if len(legend) > 0:
        plt.legend(legend)

    plot_xaxis_disperse(axis)

    try:
        if save_fig:
            temp_path = os.path.join("output", "temp")
            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return

            filename = os.path.join(temp_path, filename)
            if os.path.exists(filename):
                os.remove(filename)

            plt.savefig(filename)

        else:
            plt.show()

    except: # pylint: disable=bare-except
        print(
            f"{WARNING}Warning: plot failed to render in 'specialty plotting' " +
            f"of title: {title}{NORMAL}")

    plt.close('all')
    plt.clf()
