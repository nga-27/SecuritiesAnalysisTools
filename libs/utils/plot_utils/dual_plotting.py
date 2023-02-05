import os

from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt

from libs.utils import dates_extractor_list

from .utils import plot_xaxis_disperse, WARNING, NORMAL, is_data_list


def dual_plotting(y_list_1: list, y_list_2: list, y1_label: str, y2_label: str, **kwargs):
    """Dual Plotting

    Plot two different scales of y-values against same x-axis. Both y scales can be sets
    of values, so y1 and y2 can be list of lists. Great use for a fund's price versus various
    oscillators and metrics with y-values far different than the prices.

    Arguments:
        y1 {list} -- y-value data to be plotted on y1-axis, can be list of lists
        y2 {list} -- y-value data to be plotted on y2-axis, can be list of lists
        y1_label {str} -- label for y1 axis
        y2_label {str} -- label for y2 axis

    Optional Args:
        x_label {str} -- label for x axis (default: {'Trading Days'})
        x {list} -- x-value data (default: {[]}) (length of lists)
        title {str} -- title of plot (default: {''})
        legend {list} -- y2 signals (default: {[]})
        save_fig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_dual_plot.png'})
        subplot {bool} -- plots on top of eachother (default: {False})

    Returns:
        None
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    register_matplotlib_converters()

    x_label = kwargs.get('x_label', 'Trading Days')
    x_list = kwargs.get('x', [])
    title = kwargs.get('title', '')
    legend = kwargs.get('legend', [])
    save_fig = kwargs.get('save_fig', False)
    filename = kwargs.get('filename', 'temp_dual_plot.png')
    subplot = kwargs.get('subplot', False)

    if len(x_list) < 1:
        if is_data_list(y_list_1):
            x_list = dates_extractor_list(y_list_1[0])
        else:
            x_list = dates_extractor_list(y_list_1)

    fig = plt.figure()

    if subplot:
        num_plots = 2
        plots = [y_list_1]
        ylabels = [y1_label]

        if is_data_list(y_list_1):
            num_plots += len(y_list_1) - 1
        if is_data_list(y_list_2):
            num_plots += len(y_list_2) - 1
            plots.extend(y_list_2)
            ylabels.extend(y2_label)
        else:
            plots.append(y_list_2)
            ylabels.append(y2_label)

        sp_index = num_plots * 100 + 11
        for plot in range(num_plots):
            ax1 = plt.subplot(sp_index)
            plt.plot(x_list, plots[plot])
            plt.ylabel(ylabels[plot])

            if plot == 0:
                if len(title) > 0:
                    plt.title(title)

            sp_index += 1

    else:
        ax1 = plt.subplot(111)
        if is_data_list(y_list_2):
            color = 'k'
        else:
            color = 'tab:orange'
        ax1.set_xlabel(x_label)

        list_setting = False
        if is_data_list(y_list_1):
            list_setting = True
            ax1.set_ylabel(y1_label[0])

            for y_val in y_list_1:
                ax1.plot(x_list, y_val)
                ax1.tick_params(axis='y')
                ax1.grid(linestyle=':')

            plt.legend(y1_label)

        else:
            ax1.set_ylabel(y1_label, color=color)
            ax1.plot(x_list, y_list_1, color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.grid(linestyle=':')
            plt.legend([y1_label])

        ax2 = ax1.twinx()

        if list_setting:
            color = 'k'
        else:
            color = 'tab:blue'

        if is_data_list(y_list_2):
            ax2.set_ylabel(y2_label)

            for y_val in y_list_2:
                ax2.plot(x_list, y_val)
                ax2.tick_params(axis='y')
                ax2.grid()

            if len(legend) > 0:
                plt.legend(legend)
            elif isinstance(y2_label, list):
                plt.legend(y2_label)
            else:
                plt.legend([y2_label])

        else:
            ax2.set_ylabel(y2_label, color=color)
            ax2.plot(x_list, y_list_2, color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            ax2.grid()
            plt.legend([y2_label])

        if len(title) > 0:
            plt.title(title)

    plt.tight_layout()
    plot_xaxis_disperse(ax1)

    try:
        if save_fig:
            temp_path = os.path.join("output", "temp")
            filename = os.path.join(temp_path, filename)

            if not os.path.exists(temp_path):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return

            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename, bbox_inches="tight")

        else:
            # Case of functions, show the plot and not save it.
            plt.show()

    except: # pylint: disable=bare-except
        print(
            f"{WARNING} Warning: plot failed to render in 'dual_plotting' of title: " +
            f"{title}{NORMAL}")

    plt.close('all')
    plt.clf()