""" bar_charting """
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt

from .utils import plot_xaxis_disperse, save_or_render_plot


def bar_chart(data: list, **kwargs):
    """Bar Chart

    Exclusively used for MACD, On Balance Volume, Awesome Oscillator

    Arguments:
        data {list} -- list of y-values to be plotted

    Optional Args:
        x {list} -- x-value data (default: {[]}) (length of lists)
        position {pd.DataFrame} -- fund data, plotted as normal plot (default: {[]})
        title {str} -- title of plot (default: {''})
        save_fig {bool} -- True will save as 'filename' (default: {False})
        filename {str} -- path to save plot (default: {'temp_bar_chart.png'})
        positive {bool} -- True plots all color bars positively (default: {False})
        bar_delta {bool} -- True: y[i] > y[i-1] -> green, else red (default: {False})

    Returns:
        None
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    register_matplotlib_converters()

    x_list = kwargs.get('x', [])
    position = kwargs.get('position', [])
    title = kwargs.get('title', '')
    save_fig = kwargs.get('save_fig', False)
    filename = kwargs.get('filename', 'temp_bar_chart.png')
    all_positive = kwargs.get('all_positive', False)
    bar_delta = kwargs.get('bar_delta', False)

    if len(x_list) < 1:
        x_list = list(range(len(data)))

    colors = []
    positive = []
    bar_awesome = []

    for i, bar_data in enumerate(data):
        if bar_data > 0.0:
            positive.append(bar_data)
            colors.append('green')
        elif bar_data < 0.0:
            positive.append(-1.0 * bar_data)
            colors.append('red')
        else:
            positive.append(bar_data)
            colors.append('black')

        if i == 0:
            bar_awesome.append(colors[-1])
        else:
            if bar_data < data[i-1]:
                bar_awesome.append('red')
            elif bar_data > data[i-1]:
                bar_awesome.append('green')
            else:
                bar_awesome.append(bar_awesome[-1])

    if all_positive:
        data = positive

    fig, ax1 = plt.subplots()
    if bar_delta:
        barlist = ax1.bar(x_list, data, width=1, color=bar_awesome)
    else:
        barlist = ax1.bar(x_list, data, width=1, color=colors)

    if not bar_delta:
        for i in range(1, len(data)):
            if data[i] > 0.0:
                if data[i] < data[i-1]:
                    barlist[i].set_alpha(0.3)
            else:
                if data[i] > data[i-1]:
                    barlist[i].set_alpha(0.3)

    plt.title(title)
    if len(position) > 0:
        ax2 = ax1.twinx()
        ax2.plot(position['Close'])

    plot_xaxis_disperse(ax1)
    save_or_render_plot(plt, fig, save_fig, title, filename, 'bar chart')
    plt.close('all')
    plt.clf()
