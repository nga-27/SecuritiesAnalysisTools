import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
from datetime import datetime
import os
from pandas.plotting import register_matplotlib_converters

from .formatting import dates_extractor_list


def plot_xaxis_disperse(axis_obj, every_nth: int=2, dynamic=True):
    num_ticks = len(axis_obj.xaxis.get_ticklabels())
    tick_even = True
    if dynamic:
        if num_ticks % 2 == 0:
            # length is even, end with tick mark
            tick_even = True
        else:
            tick_even = False

    for n, label in enumerate(axis_obj.xaxis.get_ticklabels()):
        if tick_even:
            if n % every_nth == 0:
                label.set_visible(False)
        else:
            if n % every_nth != 0:
                label.set_visible(False)
    return 


def dual_plotting(
    y1: list, 
    y2: list, 
    y1_label: str, 
    y2_label: str, 
    x_label: str='trading days',
    x=[],
    title='', 
    saveFig=False,
    filename='temp.png'):

    register_matplotlib_converters()
    if len(x) < 1:
        x = dates_extractor_list(y1)

    fig, ax1 = plt.subplots()
    color = 'tab:orange'
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y1_label, color=color)
    ax1.plot(x, y1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(linestyle=':')
    plt.legend([y1_label])

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel(y2_label, color=color)
    ax2.plot(x, y2, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid()

    fig.tight_layout()
    plt.legend([y2_label])

    plt.tight_layout()
    plot_xaxis_disperse(ax1)

    if len(title) > 0:
        plt.title(title)

    try:
        if saveFig:
            filename = 'output/temp/' + filename
            if not os.path.exists('output/temp/'):
                # For functions, this directory may not exist.
                plt.close(fig)
                plt.clf()
                return 
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"plot failed to render in 'dual_plotting' of title: {title}")
    plt.close('all')
    plt.clf()


def generic_plotting(list_of_plots: list, x_=[], colors=[], title='', legend=[], saveFig=False, filename=''):
    register_matplotlib_converters()

    if len(colors) > 0:
        if len(colors) != len(list_of_plots):
            print(f"Warning: lengths of plots ({len(list_of_plots)}) and colors ({len(colors)}) do not match in generic_plotting.")
            return None

    fig, ax = plt.subplots()
    
    if len(x_) < 1:
        x = dates_extractor_list(list_of_plots[0])
        for i, fig in enumerate(list_of_plots):
            if len(colors) > 0:
                plt.plot(x, fig, colors[i])
            else:
                plt.plot(x, fig)
    else:
        if type(x_[0]) == list:
            x = x_
            for i in range(len(list_of_plots)):
                if len(colors) > 0:
                    plt.plot(x[i], list_of_plots[i], colors[i])
                else:
                    plt.plot(x[i], list_of_plots[i])
        else:
            x = x_
            for i, figy in enumerate(list_of_plots):
                if len(colors) > 0:
                    plt.plot(x, figy, colors[i])
                else:
                    plt.plot(x, figy)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"plot failed to render in 'generic_plotting' of title: {title}")
    plt.close('all')
    plt.clf()


def histogram(data: list, position: pd.DataFrame='', bins=None, saveFig=False, filename=''):
    """ Currently unused - Primarily used for MACD """
    if bins is None:
        bins = len(data)
    plt.hist(data, bins=bins)

    if len(position) > 0:
        plt.plot(position['Close'])

    try:
        if saveFig:
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"plot failed to render in 'histogram'")
    plt.close()
    plt.clf()


def bar_chart(data: list, x_=[], position: pd.DataFrame='', name='', saveFig=False, filename=''):
    """ Exclusively used for MACD """
    if len(x_) < 1:
        x = list(range(len(data)))
    else:
        x = x_
    
    colors = []
    for bar in data:
        if bar > 0.0:
            colors.append('green')
        else:
            colors.append('red')

    fig, ax1 = plt.subplots()
    barlist = ax1.bar(x, data, width=1, color=colors)
    for i in range(1,len(data)):
        if data[i] > 0.0:
            if data[i] < data[i-1]:
                barlist[i].set_alpha(0.3)
        else:
            if data[i] > data[i-1]:
                barlist[i].set_alpha(0.3)
    plt.title(name)

    if len(position) > 0:
        ax2 = ax1.twinx()
        ax2.plot(position['Close'])

    plot_xaxis_disperse(ax1)

    try:
        if saveFig:
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"plot failed to render in 'bar_chart' of name: {name}")
    plt.close()
    plt.clf()



def specialty_plotting(list_of_plots: list, x_=[], alt_ax_index=[], title='', legend=[], saveFig=False, filename=''):
    register_matplotlib_converters()
    x = x_
    if len(x_) < 1:
        x = dates_extractor_list(list_of_plots[0])
    fig, ax = plt.subplots()

    for i in range(len(list_of_plots)):
        if i not in alt_ax_index:
            ax.plot(x, list_of_plots[i])
    
    ax2 = ax.twinx()
    for i in range(len(list_of_plots)):
        if i in alt_ax_index:
            ax2.plot(x, list_of_plots[i], color='tab:purple')

    plt.title(title)
    ax2.set_ylabel(legend[0])
    if len(legend) > 0:
        plt.legend(legend)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"plot failed to render in 'specialty plotting' of title: {title}")
    plt.close()
    plt.clf()


def shape_plotting(main_plot: pd.DataFrame, shapeXY: list=[], feature='default', title='', legend=[], saveFig=False, filename=''):
    """ Note, shapeXY is a list of dictionaries of coordinates and type """
    register_matplotlib_converters()

    fig, ax = plt.subplots()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    x = [datetime.strptime(d, '%Y-%m-%d').date() for d in main_plot.index.astype(str)]
    plt.plot(x, main_plot)

    # if type(main_plot) != list:
    #     new_list = []
    #     for i in range(len(main_plot)):
    #         new_list.append(main_plot[i])
    #     main_plot = new_list

    # plt.plot(main_plot)
    xpts = plt.gca().get_lines()[0].get_xdata()
    ypts = plt.gca().get_lines()[0].get_ydata()
    """ CONVERT SHAPEXY (DICT OF ITEMS) TO DATE """

    if feature == 'default':
        dotted_line = plt.Line2D((xpts[40],xpts[len(xpts)-40]), (np.min(ypts), np.max(ypts)), lw=1, ls='-', alpha=0.5)
        plt.gca().add_line(dotted_line)

    elif (feature == 'head_and_shoulders') and (shapeXY != []):
        for shape in shapeXY:
            
            y_shp_pts = []
            x_shp_pts = []
            if shape['type'] == 'bullish':
                colors = 'green'
            else:
                colors = 'red'

            for pt in shape['indexes']:
                # convert to date here
                y_shp_pts.append(pt[1])
                x_shp_pts.append(xpts[pt[0]])
            box = plt.Line2D((x_shp_pts[0], x_shp_pts[4]), (np.min(y_shp_pts), np.min(y_shp_pts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)
            box = plt.Line2D((x_shp_pts[0], x_shp_pts[0]), (np.min(y_shp_pts), np.max(y_shp_pts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)
            box = plt.Line2D((x_shp_pts[0], x_shp_pts[4]), (np.max(y_shp_pts), np.max(y_shp_pts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)
            box = plt.Line2D((x_shp_pts[4], x_shp_pts[4]), (np.min(y_shp_pts), np.max(y_shp_pts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"plot failed to render in 'shape plotting' of title: {title}")
    plt.close()
    plt.clf()


def candlestick(data: pd.DataFrame, title='', legend=[], saveFig=False, filename=''):
    register_matplotlib_converters()

    fig, ax = plt.subplots()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    x = [datetime.strptime(d, '%Y-%m-%d').date() for d in data.index.astype(str)]
    plt.plot(x, data['Close'], alpha=0.01)
    
    for i in range(len(data['Close'])):
        op = data['Open'][i]
        close = data['Close'][i]
        high = data['High'][i]
        low = data['Low'][i]

        if data['Close'][i] > data['Open'][i]:
            colors = 'green'
        elif data['Close'][i] == data['Open'][i]:
            colors = 'black'
            if i > 0:
                op = data['Open'][i-1]
                if op > close:
                    colors = 'red'
                else: 
                    colors = 'green'
        else:
            colors = 'red'
        oc = plt.Line2D((x[i], x[i]), (op, close), lw=3, ls='-', alpha=1, color=colors)
        plt.gca().add_line(oc)
        hl = plt.Line2D((x[i], x[i]), (high, low), lw=0.75, ls='-', alpha=1, color='black')
        plt.gca().add_line(hl)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)

    plot_xaxis_disperse(ax)

    try:
        if saveFig:
            filename = 'output/temp/' + filename
            if os.path.exists(filename):
                os.remove(filename)
            plt.savefig(filename)
        else:
            plt.show()
    except:
        print(f"plot failed to render in 'shape plotting' of title: {title}")
    plt.close()
    plt.clf()
