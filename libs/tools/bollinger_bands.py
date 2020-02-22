import pandas as pd
import numpy as np

from libs.utils import ProgressBar
from libs.utils import generic_plotting, dual_plotting, SP500

from .moving_average import simple_moving_avg, exponential_moving_avg


def volatility_calculation(position: pd.DataFrame, **kwargs):

    plot_output = kwargs.get('plot_output', True)
    periods = [20, 50, 100, 250]
    stdevs = []
    for _ in range(len(periods)):
        std = [0.0] * len(position['Close'])
        stdevs.append(std)

    typical_price = []
    for i, close in enumerate(position['Close']):
        typical_price.append(
            (close + position['Low'][i] + position['High'][i]) / 3.0)

    for i, period in enumerate(periods):
        for j in range(period, len(typical_price)):
            std = np.std(typical_price[j-(period): j])
            stdevs[i][j] = std

    std_correction = []
    for j in range(len(typical_price)):
        s = 0.35 * stdevs[3][j] + 0.3 * stdevs[2][j] + \
            0.2 * stdevs[1][j] + 0.15 * stdevs[0][j]
        std_correction.append(s)

    if plot_output:
        dual_plotting(position['Close'], std_correction, 'Price',
                      'Volatility', title='Bollinger Volatility')


def get_bollinger_signals(position: pd.DataFrame, period: int, stdev: float, **kwargs) -> dict:
    """Get Bollinger Band Signals

    Arguments:
        position {pd.DataFrame} -- dataset
        period {int} -- time frame for moving average
        stdev {float} -- multiplier for band range

    Optional Args:
        plot_output {bool} -- (default: {True})
        filter_type {str} -- type of moving average (default: {'simple'})
        name {str} -- (default: {''})

    Returns:
        dict -- bollinger band data object
    """
    filter_type = kwargs.get('filter_type', 'simple')
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')

    typical_price = []
    for i, close in enumerate(position['Close']):
        typical_price.append(
            (close + position['Low'][i] + position['High'][i]) / 3.0)

    if filter_type == 'exponential':
        ma = exponential_moving_avg(typical_price, period, data_type='list')
    else:
        ma = simple_moving_avg(typical_price, period, data_type='list')

    upper = ma.copy()
    lower = ma.copy()
    std_list = [0.0] * len(ma)
    for i in range(period, len(ma)):
        std = np.std(typical_price[i-(period): i])
        std_list[i] = std
        upper[i] = ma[i] + (stdev * std)
        lower[i] = ma[i] - (stdev * std)

    signals = {'upper_band': upper, 'lower_band': lower}

    name3 = SP500.get(name, name)
    name2 = name3 + ' - Bollinger Bands'
    if plot_output:
        generic_plotting([position['Close'], ma, upper, lower],
                         title=name2, x=position.index,
                         legend=['Price', 'Moving Avg', 'Upper Band', 'Lower Band'])

    else:
        filename = name + f'/bollinger_bands_{name}.png'
        generic_plotting([position['Close'], ma, upper, lower],
                         title=name2, x=position.index,
                         legend=['Price', 'Moving Avg',
                                 'Upper Band', 'Lower Band'],
                         saveFig=True, filename=filename)

    return signals


def bollinger_bands(position: pd.DataFrame, **kwargs) -> dict:
    """Bollinger Bands

    Arguments:
        position {pd.DataFrame} -- dataset

    Optional Args:
        period {int} -- day moving average [10, 20, 50] (default: {20})
        stdev {float} -- stdev of signal [1.5, 2.0, 2.5] (default: {2.0})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- bollinger bands data object
    """
    period = kwargs.get('period', 20)
    stdev = kwargs.get('stdev', 2.0)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')

    bb = dict()

    bb['tabular'] = get_bollinger_signals(
        position, period, stdev, plot_output=plot_output, name=name)

    volatility_calculation(position, plot_output=plot_output)
    p_bar.uptick(increment=1.0)

    return bb
