import pandas as pd
import numpy as np

from libs.utils import ProgressBar
from libs.utils import generic_plotting, dual_plotting, SP500
from libs.features import normalize_signals

from .moving_average import simple_moving_avg, exponential_moving_avg, windowed_moving_avg


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
        view {str} -- directory of plots (default: {''})

    Returns:
        dict -- bollinger bands data object
    """
    period = kwargs.get('period', 20)
    stdev = kwargs.get('stdev', 2.0)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')
    view = kwargs.get('view', '')

    if period == 10:
        stdev = 1.5
    if period == 50:
        stdev = 2.5

    bb = dict()

    bb['tabular'] = get_bollinger_signals(
        position, period, stdev, plot_output=plot_output, name=name, view=view)

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    bb['volatility'] = volatility_calculation(
        position, plot_output=plot_output, view=view)

    if p_bar is not None:
        p_bar.uptick(increment=0.3)

    bb = bollinger_indicators(position, bb, period=period)

    if p_bar is not None:
        p_bar.uptick(increment=0.3)

    bb = bollinger_metrics(position, bb, period=period,
                           plot_output=plot_output, name=name, view=view)

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    bb['type'] = 'oscillator'

    return bb


def bollinger_metrics(position: pd.DataFrame, bol_bands: dict, **kwargs) -> dict:
    """Bollinger Metrics

    Arguments:
        position {pd.DataFrame} -- dataset of fund
        bol_bands {dict} -- bollinger band data object

    Optional Args:
        period {int} -- look back period for Stdev (default: {20})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})

    Returns:
        dict -- bollinger band data object
    """
    period = kwargs.get('period', 20)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view')

    weights = [1.0, 0.6, 0.25, 0.0]
    tot_len = len(position['Close'])

    metrics = [0.0] * tot_len
    for feat in bol_bands['indicators']:
        ind = feat['index']
        if feat['type'] == 'bullish':
            val = 1.0
        else:
            val = -1.0

        metrics[ind] += val * weights[0]

        # Smooth the curves
        if ind - 1 >= 0:
            metrics[ind-1] += val * weights[1]
        if ind + 1 < tot_len:
            metrics[ind+1] += val * weights[1]
        if ind - 2 >= 0:
            metrics[ind-2] += val * weights[2]
        if ind + 2 < tot_len:
            metrics[ind+2] += val * weights[2]
        if ind - 3 >= 0:
            metrics[ind-3] += val * weights[3]
        if ind + 3 < tot_len:
            metrics[ind+3] += val * weights[3]

    close = position['Close']
    bb = bol_bands['tabular']
    for i in range(period, len(close)):
        s_range = bb['middle_band'][i] - bb['lower_band'][i]
        if metrics[i] <= 0.6 and metrics[i] >= -0.6:
            c = close[i] - bb['middle_band'][i]
            c = np.round(c / s_range, 4)
            metrics[i] = c

    metrics = windowed_moving_avg(metrics, 7, data_type='list')
    norm_signal = normalize_signals([metrics])[0]

    bol_bands['metrics'] = norm_signal

    name3 = SP500.get(name, name)
    name2 = name3 + f" - Bollinger Band Metrics"
    if plot_output:
        dual_plotting(position['Close'], norm_signal, 'Price',
                      'Indicators', title=name2)
    else:
        filename = name + f"/{view}" + f"/bollinger_band_metrics_{name}.png"
        dual_plotting(position['Close'], norm_signal, 'Price',
                      'Metrics', title=name2, saveFig=True, filename=filename)

    return bol_bands


def bollinger_indicators(position: pd.DataFrame, bol_bands: dict, **kwargs) -> dict:
    """Bollinger Indicators 

    (https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands)

    Arguments:
        position {pd.DataFrame} -- dataset
        bol_bands {dict} -- bol bands data object

    Returns:
        dict -- bol bands data object
    """
    period = kwargs.get('period', 20)

    bol_bands['indicators'] = find_W_bottom(position, bol_bands, period)

    bol_bands['indicators'].extend(find_M_top(position, bol_bands, period))

    bol_bands = get_extremes_ratios(position, bol_bands, period=period)

    return bol_bands


def volatility_calculation(position: pd.DataFrame, **kwargs) -> list:
    """Volatility Calculation

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})

    Returns:
        list -- volatility data as list of weighted standard deviations
    """
    plot_output = kwargs.get('plot_output', True)

    periods = [50, 100, 250, 500]
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
            std = np.std(typical_price[j-(period): j]) * 2.0
            stdevs[i][j] = std

    std_correction = []
    for j in range(len(typical_price)):
        if j < periods[1]:
            s = stdevs[0][j]
        elif j < periods[2]:
            s = 0.7 * stdevs[1][j] + 0.3 * stdevs[0][j]
        elif j < periods[3]:
            s = 0.55 * stdevs[2][j] + \
                0.3 * stdevs[1][j] + 0.15 * stdevs[0][j]
        else:
            s = 0.4 * stdevs[3][j] + 0.3 * stdevs[2][j] + \
                0.2 * stdevs[1][j] + 0.1 * stdevs[0][j]
        std_correction.append(s)

    for i, price in enumerate(typical_price):
        std_correction[i] = std_correction[i] / price

    if plot_output:
        dual_plotting(position['Close'], std_correction, 'Price',
                      'Volatility', title='Standard Deviation Volatility')

    return std_correction


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
        view {str} -- (default: {None})

    Returns:
        dict -- bollinger band data object
    """
    filter_type = kwargs.get('filter_type', 'simple')
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view')

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

    signals = {'upper_band': upper, 'lower_band': lower, 'middle_band': ma}

    name3 = SP500.get(name, name)
    name2 = name3 + ' - Bollinger Bands'
    if plot_output:
        generic_plotting([position['Close'], ma, upper, lower],
                         title=name2, x=position.index,
                         legend=['Price', 'Moving Avg', 'Upper Band', 'Lower Band'])

    else:
        filename = name + f"/{view}" + f'/bollinger_bands_{name}.png'
        generic_plotting([position['Close'], ma, upper, lower],
                         title=name2, x=position.index,
                         legend=['Price', 'Moving Avg',
                                 'Upper Band', 'Lower Band'],
                         saveFig=True, filename=filename)

    return signals


### Metrics Indicator Determinations ###

def find_W_bottom(position: pd.DataFrame, bol_bands: dict, period: int) -> list:
    """Find the 'W' shape bottom

    Arguments:
        position {pd.DataFrame} -- fund dataset
        bol_bands {dict} -- bollinger bands data object
        period {int} -- look back period for bollinger band

    Returns:
        list -- list of 'W' detected bottoms
    """
    w_list = []
    bb = bol_bands['tabular']

    state = 'n'
    prices = [0.0, 0.0, 0.0]
    close = position['Close']
    for i in range(period, len(close)):

        if (state == 'n') and (close[i] <= bb['lower_band'][i]):
            state = 'w1'
            prices[0] = close[i]

        elif (state == 'w1'):
            if close[i] < prices[0]:
                prices[0] = close[i]
            else:
                state = 'w2'

        elif (state == 'w2'):
            if close[i] >= bb['middle_band'][i]:
                prices[1] = close[i]
                state = 'w3'
            elif close[i] < prices[0]:
                prices[0] = close[i]
                state = 'w1'

        elif (state == 'w3'):
            if close[i] > prices[1]:
                prices[1] = close[i]
            else:
                state = 'w4'

        elif state == 'w4':
            if close[i] < prices[0]:
                prices[2] = close[i]
                state = 'w5'
            elif close[i] <= bb['lower_band'][i]:
                state = 'w1'
            elif close[i] > prices[1]:
                prices[1] = close[i]
                state = 'w3'

        elif state == 'w5':
            if close[i] < prices[2]:
                prices[2] = close[i]
                if close[i] <= bb['lower_band'][i]:
                    state = 'w1'
            else:
                state = 'w6'

        elif state == 'w6':
            if close[i] > prices[1]:
                # Breakout signalling W completion!
                w_list.append({'index': i, 'type': 'bullish', 'style': 'W'})
                state = 'n'
            elif close[i] < prices[2]:
                prices[2] = close[i]
                state = 'w5'
                if close[i] <= bb['lower_band'][i]:
                    state = 'w1'

    return w_list


def get_extremes_ratios(position: pd.DataFrame, bol_bands: dict, **kwargs) -> dict:

    period = kwargs.get('period', 20)
    bb = bol_bands['tabular']

    state = 'n'
    close = position['Close']
    for i in range(period, len(close)):

        if state == 'n':
            if close[i] < bb['middle_band'][i]:
                state = 'e1'
            elif close[i] > bb['middle_band'][i]:
                state = 'u1'

        elif state == 'e1':
            if close[i] <= bb['lower_band'][i]:
                state = 'e2'
                bol_bands['indicators'].append(
                    {'index': i, 'type': 'bearish', 'style': 'extremes'})
            if close[i] > bb['middle_band'][i]:
                state = 'u1'

        elif state == 'e2':
            if close[i] <= bb['lower_band'][i]:
                bol_bands['indicators'].append(
                    {'index': i, 'type': 'bearish', 'style': 'extremes'})
            else:
                state = 'e3'

        elif state == 'e3':
            if close[i] >= bb['middle_band'][i]:
                state = 'u1'

        elif state == 'u1':
            if close[i] >= bb['upper_band'][i]:
                state = 'u2'
                bol_bands['indicators'].append(
                    {'index': i, 'type': 'bullish', 'style': 'extremes'})
            if close[i] < bb['middle_band'][i]:
                state = 'e1'

        elif state == 'u2':
            if close[i] >= bb['upper_band'][i]:
                bol_bands['indicators'].append(
                    {'index': i, 'type': 'bullish', 'style': 'extremes'})
            else:
                state = 'u3'

        elif state == 'u3':
            if close[i] <= bb['middle_band'][i]:
                state = 'e1'

    return bol_bands


def find_M_top(position: pd.DataFrame, bol_bands: dict, period: int) -> list:
    """Find the 'M' shape top

    Arguments:
        position {pd.DataFrame} -- fund dataset
        bol_bands {dict} -- bollinger bands data object
        period {int} -- look back period for bollinger band

    Returns:
        list -- list of 'M' detected tops
    """
    m_list = []
    bb = bol_bands['tabular']

    state = 'n'
    prices = [0.0, 0.0, 0.0]
    close = position['Close']
    for i in range(period, len(close)):

        if (state == 'n') and (close[i] > bb['upper_band'][i]):
            state = 'w1'
            prices[0] = close[i]

        elif (state == 'w1'):
            if close[i] > prices[0]:
                prices[0] = close[i]
            else:
                state = 'w2'

        elif (state == 'w2'):
            if close[i] <= bb['middle_band'][i]:
                prices[1] = close[i]
                state = 'w3'
            elif close[i] > prices[0]:
                prices[0] = close[i]
                state = 'w1'

        elif (state == 'w3'):
            if close[i] < prices[1]:
                prices[1] = close[i]
            else:
                state = 'w4'

        elif state == 'w4':
            if close[i] > prices[0]:
                prices[2] = close[i]
                state = 'w5'
            elif close[i] >= bb['upper_band'][i]:
                state = 'w1'
            elif close[i] < prices[1]:
                prices[1] = close[i]
                state = 'w3'

        elif state == 'w5':
            if close[i] > prices[2]:
                prices[2] = close[i]
                if close[i] >= bb['upper_band'][i]:
                    state = 'w1'
            else:
                state = 'w6'

        elif state == 'w6':
            if close[i] < prices[1]:
                # Breakout signalling M completion!
                m_list.append({'index': i, 'type': 'bearish', 'style': 'M'})
                state = 'n'
            elif close[i] > prices[2]:
                prices[2] = close[i]
                state = 'w5'
                if close[i] >= bb['upper_band'][i]:
                    state = 'w1'

    return m_list
