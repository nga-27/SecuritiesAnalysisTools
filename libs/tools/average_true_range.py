import os
import pandas as pd
import numpy as np

from libs.utils import dual_plotting, INDEXES
from libs.utils import ProgressBar
from .moving_average import exponential_moving_avg


def average_true_range(fund: pd.DataFrame, **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar = kwargs.get('progress_bar')

    atr = dict()
    atr['tabular'] = get_atr_signal(
        fund, plot_output=plot_output, name=name, views=views)

    atr = atr_indicators(fund, atr, plot_output=plot_output, name=name)

    if p_bar is not None:
        p_bar.uptick(increment=1.0)

    return atr


def get_atr_signal(fund: pd.DataFrame, **kwargs) -> list:
    """Get ATR Signal

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        period {int} -- lookback period of atr signal (default: {14})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})

    Returns:
        list -- atr signal
    """
    period = kwargs.get('period', 14)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')

    signal = [0.0] * len(fund['Close'])

    atr = [0.0]
    for i in range(1, len(fund['Close'])):
        trues = [
            fund['High'][i] - fund['Low'][i],
            abs(fund['High'][i] - fund['Close'][i-1]),
            abs(fund['Low'][i] - fund['Close'][i-1])
        ]
        _max = max(trues)
        atr.append(_max)

    for i in range(period-1, len(fund['Close'])):
        atr_val = sum(atr[i-(period-1):i+1]) / float(period)
        signal[i] = atr_val

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Average True Range"
    if plot_output:
        dual_plotting(fund['Close'], signal, 'Price', 'ATR', title=title)
    else:
        filename = os.path.join(name, views, f"atr_{name}.png")
        dual_plotting(fund['Close'], signal, 'Price', 'ATR',
                      title=title, saveFig=True, filename=filename)

    return signal


def atr_indicators(fund: pd.DataFrame, atr_dict: dict, **kwargs) -> dict:
    """ATR Indicators

    Run exponential moving average periods to weed out higher volatility: 20, 40

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        atr_dict {dict} -- atr data object

    Optional Args:
        periods {list} -- list of ema lookback periods (default: {[20, 40]})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})

    Returns:
        dict: [description]
    """
    periods = kwargs.get('periods', [50, 200])
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')

    ema_1 = exponential_moving_avg(
        atr_dict['tabular'], periods[0], data_type='list')
    ema_2 = exponential_moving_avg(
        atr_dict['tabular'], periods[1], data_type='list')

    if plot_output:
        name2 = INDEXES.get(name, name)
        title = f"{name2} - ATR Moving Averages"
        dual_plotting(fund['Close'], [atr_dict['tabular'],
                                      ema_1, ema_2], 'Price', 'ATRs', title=title)

    return atr_dict
