import os
import pandas as pd
import numpy as np

from libs.utils import dual_plotting, ProgressBar
from libs.utils import INDEXES
from .rate_of_change import roc_signal
from .moving_average import simple_moving_avg


def know_sure_thing(fund: pd.DataFrame, **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar = kwargs.get('progress_bar')

    kst = dict()
    signal, signal_line = kst_signal(
        fund, plot_output=plot_output, name=name, views=views)

    kst['tabular'] = {'signal': signal, 'signal_line': signal_line}

    if p_bar is not None:
        p_bar.uptick(increment=1.0)

    return kst


def kst_signal(fund: pd.DataFrame, **kwargs) -> list:

    periods = kwargs.get('periods', [10, 15, 20, 30])
    sma_intervals = kwargs.get('sma_intervals', [10, 10, 10, 15])
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')

    signal = [0.0] * len(fund['Close'])

    for i, period in enumerate(periods):
        roc = roc_signal(fund, period)
        sma = simple_moving_avg(roc, sma_intervals[i], data_type='list')

        for j in range(len(signal)):
            signal[j] += float(i + 1) * sma[j]

    signal_line = simple_moving_avg(signal, 9, data_type='list')

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Know Sure Thing"

    if plot_output:
        dual_plotting(fund['Close'], [signal, signal_line],
                      'Price', 'KST', title=title)
    else:
        filename = os.path.join(name, views, f"kst_oscillator_{name}")
        dual_plotting(fund['Close'], [signal, signal_line], 'Price',
                      'KST', title=title, saveFig=True, filename=filename)

    return signal, signal_line
