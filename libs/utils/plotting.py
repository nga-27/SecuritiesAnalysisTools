import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

def dual_plotting(
    y1: list, 
    y2: list, 
    y1_label: str, 
    y2_label: str, 
    x_label: str='trading days', 
    title='', 
    saveFig=False,
    filename='temp.png'):

    fig, ax1 = plt.subplots()
    color = 'tab:orange'
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y1_label, color=color)
    ax1.plot(y1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(linestyle=':')
    plt.legend([y1_label])

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel(y2_label, color=color)
    ax2.plot(y2, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid()

    fig.tight_layout()
    plt.legend([y2_label])
    if len(title) > 0:
        plt.title(title)

    if saveFig:
        plt.savefig(filename)
    else:
        plt.show()


def generic_plotting(list_of_plots: list, title='', saveFig=False, filename=''):
    for fig in list_of_plots:
        plt.plot(fig)
    plt.title(title)

    if saveFig:
        plt.savefig(filename)
    else:
        plt.show()


def histogram(data: list, bins=None, saveFig=False, filename=''):
    """ Currently unused - Primarily used for MACD """
    if bins is None:
        bins = len(data)
    plt.hist(data, bins=bins)

    if saveFig:
        plt.savefig(filename)
    else:
        plt.show()


def bar_chart(data: list, name='', saveFig=False, filename=''):
    """ Exclusively used for MACD """
    x = list(range(len(data)))
    colors = []
    for bar in data:
        if bar > 0.0:
            colors.append('green')
        else:
            colors.append('red')
    barlist = plt.bar(x, data, width=1, color=colors)
    for i in range(1,len(data)):
        if data[i] > 0.0:
            if data[i] < data[i-1]:
                barlist[i].set_alpha(0.3)
        else:
            if data[i] > data[i-1]:
                barlist[i].set_alpha(0.3)
    plt.title(name)

    if saveFig:
        plt.savefig(filename)
    else:
        plt.show()
