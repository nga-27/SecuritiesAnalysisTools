import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 

def dual_plotting(y1: list, y2: list, y1_label: str, y2_label: str, x_label: str='trading days', title=''):
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
    plt.show()