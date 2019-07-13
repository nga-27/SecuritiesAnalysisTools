import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from datetime import datetime
import os
from pandas.plotting import register_matplotlib_converters

from .formatting import dates_extractor_list

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

    if len(title) > 0:
        plt.title(title)

    if saveFig:
        filename = 'output/temp/' + filename
        if os.path.exists(filename):
            os.remove(filename)
        plt.savefig(filename)
    else:
        plt.show()
    plt.close()
    plt.clf()


def generic_plotting(list_of_plots: list, x_=[], title='', legend=[], saveFig=False, filename=''):
    register_matplotlib_converters()
    x = x_
    if len(x_) < 1:
        x = dates_extractor_list(list_of_plots[0])
    for fig in list_of_plots:
        plt.plot(x, fig)
    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)

    if saveFig:
        filename = 'output/temp/' + filename
        if os.path.exists(filename):
            os.remove(filename)
        plt.savefig(filename)
    else:
        plt.show()
    plt.close()
    plt.clf()


def histogram(data: list, position: pd.DataFrame='', bins=None, saveFig=False, filename=''):
    """ Currently unused - Primarily used for MACD """
    if bins is None:
        bins = len(data)
    plt.hist(data, bins=bins)

    if len(position) > 0:
        plt.plot(position['Close'])

    if saveFig:
        filename = 'output/temp/' + filename
        if os.path.exists(filename):
            os.remove(filename)
        plt.savefig(filename)
    else:
        plt.show()
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

    if saveFig:
        filename = 'output/temp/' + filename
        if os.path.exists(filename):
            os.remove(filename)
        plt.savefig(filename)
    else:
        plt.show()
    plt.close()
    plt.clf()



def specialty_plotting(list_of_plots: list, x_=[], alt_ax_index=[], title='', legend=[], saveFig=False, filename=''):
    register_matplotlib_converters()
    x = x_
    if len(x_) < 1:
        x = dates_extractor_list(list_of_plots[0])
    figure, ax = plt.subplots()

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

    if saveFig:
        filename = 'output/temp/' + filename
        if os.path.exists(filename):
            os.remove(filename)
        plt.savefig(filename)
    else:
        plt.show()
    plt.close()
    plt.clf()


def shape_plotting(main_plot: list, shapeXY: list=[], feature='default', title='', legend=[], saveFig=False, filename=''):
    """ Note, shapeXY is a list of dictionaries of coordinates and type """

    if type(main_plot) != list:
        new_list = []
        for i in range(len(main_plot)):
            new_list.append(main_plot[i])
        main_plot = new_list

    plt.plot(main_plot)
    xpts = plt.gca().get_lines()[0].get_xdata()
    ypts = plt.gca().get_lines()[0].get_ydata()

    if feature == 'default':
        dotted_line = plt.Line2D((xpts[40],xpts[len(xpts)-40]), (np.min(ypts), np.max(ypts)), lw=1, ls='-', alpha=0.5)
        plt.gca().add_line(dotted_line)

    elif (feature == 'head_and_shoulders') and (shapeXY != []):
        for shape in shapeXY:
            ypts = []
            xpts = []
            if shape['type'] == 'bullish':
                colors = 'green'
            else:
                colors = 'red'

            for pt in shape['indexes']:
                ypts.append(pt[1])
                xpts.append(pt[0])
            box = plt.Line2D((xpts[0], xpts[4]), (np.min(ypts), np.min(ypts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)
            box = plt.Line2D((xpts[0], xpts[0]), (np.min(ypts), np.max(ypts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)
            box = plt.Line2D((xpts[0], xpts[4]), (np.max(ypts), np.max(ypts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)
            box = plt.Line2D((xpts[4], xpts[4]), (np.min(ypts), np.max(ypts)), lw=2, ls='-.', alpha=0.75, color=colors)
            plt.gca().add_line(box)

    plt.title(title)
    if len(legend) > 0:
        plt.legend(legend)

    if saveFig:
        filename = 'output/temp/' + filename
        if os.path.exists(filename):
            os.remove(filename)
        plt.savefig(filename)
    else:
        plt.show()
    plt.close()
    plt.clf()