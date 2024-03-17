""" Bollinger Bands """
import os

import pandas as pd
import numpy as np

from libs.utils import INDEXES, PlotType, generate_plot
from libs.features import normalize_signals

from .moving_average import simple_moving_avg, exponential_moving_avg


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

    bollinger_bands_data = {}

    bollinger_bands_data['tabular'] = get_bollinger_signals(
        position, period, stdev, plot_output=plot_output, name=name, view=view)

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    bollinger_bands_data['volatility'] = volatility_calculation(
        position, plot_output=plot_output, view=view)
    if p_bar is not None:
        p_bar.uptick(increment=0.3)

    bollinger_bands_data = bollinger_indicators(position, bollinger_bands_data, period=period)
    if p_bar is not None:
        p_bar.uptick(increment=0.3)

    bollinger_bands_data = bollinger_metrics(position, bollinger_bands_data, period=period,
                           plot_output=plot_output, name=name, view=view)
    features = bollinger_band_features(bollinger_bands_data, position, plot_output=plot_output)
    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    bollinger_bands_data['type'] = 'oscillator'
    bollinger_bands_data['signals'] = features
    bollinger_bands_data['length_of_data'] = len(bollinger_bands_data['tabular']['upper_band'])

    return bollinger_bands_data


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
    # pylint: disable=too-many-locals
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
    bollinger_bands_tabular = bol_bands['tabular']
    for i in range(period, len(close)):
        s_range = bollinger_bands_tabular['middle_band'][i] - \
            bollinger_bands_tabular['lower_band'][i]
        if metrics[i] <= 0.6 and metrics[i] >= -0.6:
            val = close[i] - bollinger_bands_tabular['middle_band'][i]
            val = np.round(val / s_range, 4)
            metrics[i] = val

    metrics = exponential_moving_avg(metrics, 7, data_type='list')
    norm_signal = normalize_signals([metrics])[0]

    bol_bands['metrics'] = norm_signal

    name3 = INDEXES.get(name, name)
    name2 = name3 + " - Bollinger Band Metrics"
    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **{
            "y_list_2": norm_signal, "y1_label": 'Price', "y2_label": 'Indicators', "title": name2,
            "plot_output": plot_output, "filename": os.path.join(
                name, view, f"bollinger_band_metrics_{name}.png")
        }
    )

    return bol_bands


def bollinger_indicators(position: pd.DataFrame, bol_bands: dict, **kwargs) -> dict:
    """Bollinger Indicators

    (https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands)

    Arguments:
        position {pd.DataFrame} -- dataset
        bol_bands {dict} -- bol bands data object

    Optional Args:
        period {int} -- period to search for indicators {default: 20}

    Returns:
        dict -- bol bands data object
    """
    period = kwargs.get('period', 20)
    bol_bands['indicators'] = find_w_shape_bottom(position, bol_bands, period)
    bol_bands['indicators'].extend(find_m_shape_top(position, bol_bands, period))
    bol_bands = get_extremes_ratios(position, bol_bands, period=period)

    return bol_bands


def bollinger_band_features(bol_bands: dict, position: pd.DataFrame, plot_output=False) -> list:
    """Bollinger Band Features

    Arguments:
        bol_bands {dict} -- bollinger bands data object
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of bollinger band feature dictionaries
    """
    features = []
    for indicator in bol_bands['indicators']:
        date = position.index[indicator['index']].strftime("%Y-%m-%d")
        data = {
            "type": indicator['type'],
            "value": f"{indicator['style']} feature detection",
            "index": indicator['index'],
            "date": date
        }
        features.append(data)

        if plot_output:
            print(f"Bollinger Band: {data}")

    return features


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
            std_val = stdevs[0][j]
        elif j < periods[2]:
            std_val = 0.7 * stdevs[1][j] + 0.3 * stdevs[0][j]
        elif j < periods[3]:
            std_val = 0.55 * stdevs[2][j] + \
                0.3 * stdevs[1][j] + 0.15 * stdevs[0][j]
        else:
            std_val = 0.4 * stdevs[3][j] + 0.3 * stdevs[2][j] + \
                0.2 * stdevs[1][j] + 0.1 * stdevs[0][j]
        std_correction.append(std_val)

    for i, price in enumerate(typical_price):
        std_correction[i] = std_correction[i] / price

    if plot_output:
        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **dict(
                y_list_2=std_correction, y1_label='Price', y2_label='Volatility',
                title='Standard Deviation Volatility'
            )
        )

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
    # pylint: disable=too-many-locals
    filter_type = kwargs.get('filter_type', 'simple')
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view')

    typical_price = []
    for i, close in enumerate(position['Close']):
        typical_price.append(
            (close + position['Low'][i] + position['High'][i]) / 3.0)

    if filter_type == 'exponential':
        moving_average = exponential_moving_avg(typical_price, period, data_type='list')
    else:
        moving_average = simple_moving_avg(typical_price, period, data_type='list')

    upper = moving_average.copy()
    lower = moving_average.copy()
    std_list = [0.0] * len(moving_average)
    for i in range(period, len(moving_average)):
        std = np.std(typical_price[i-(period): i])
        std_list[i] = std
        upper[i] = moving_average[i] + (stdev * std)
        lower[i] = moving_average[i] - (stdev * std)

    signals = {'upper_band': upper, 'lower_band': lower, 'middle_band': moving_average}

    name3 = INDEXES.get(name, name)
    name2 = name3 + ' - Bollinger Bands'
    generate_plot(
        PlotType.GENERIC_PLOTTING, [position['Close'], moving_average, upper, lower], **dict(
            title=name2, x=position.index,
            legend=['Price', 'Moving Avg', 'Upper Band', 'Lower Band'], plot_output=plot_output,
            filename=os.path.join(name, view, f"bollinger_bands_{name}.png")
        )
    )

    return signals


### Metrics Indicator Determinations ###

def find_w_shape_bottom(position: pd.DataFrame, bol_bands: dict, period: int) -> list:
    """Find the 'W' shape bottom

    Arguments:
        position {pd.DataFrame} -- fund dataset
        bol_bands {dict} -- bollinger bands data object
        period {int} -- look back period for bollinger band

    Returns:
        list -- list of 'W' detected bottoms
    """
    # pylint: disable=too-many-branches,too-many-statements
    w_list = []
    bb_tabular_data = bol_bands['tabular']

    state = 'n'
    prices = [0.0, 0.0, 0.0]
    close = position['Close']
    for i in range(period, len(close)):

        if (state == 'n') and (close[i] <= bb_tabular_data['lower_band'][i]):
            state = 'w1'
            prices[0] = close[i]

        elif state == 'w1':
            if close[i] < prices[0]:
                prices[0] = close[i]
            else:
                state = 'w2'

        elif state == 'w2':
            if close[i] >= bb_tabular_data['middle_band'][i]:
                prices[1] = close[i]
                state = 'w3'
            elif close[i] < prices[0]:
                prices[0] = close[i]
                state = 'w1'

        elif state == 'w3':
            if close[i] > prices[1]:
                prices[1] = close[i]
            else:
                state = 'w4'

        elif state == 'w4':
            if close[i] < prices[0]:
                prices[2] = close[i]
                state = 'w5'
            elif close[i] <= bb_tabular_data['lower_band'][i]:
                state = 'w1'
            elif close[i] > prices[1]:
                prices[1] = close[i]
                state = 'w3'

        elif state == 'w5':
            if close[i] < prices[2]:
                prices[2] = close[i]
                if close[i] <= bb_tabular_data['lower_band'][i]:
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
                if close[i] <= bb_tabular_data['lower_band'][i]:
                    state = 'w1'

    return w_list


def get_extremes_ratios(position: pd.DataFrame, bol_bands: dict, **kwargs) -> dict:
    """Get Extremes Ratios

    Look for extreme (upper/lower band crossovers) features

    Arguments:
        position {pd.DataFrame} -- fund dataset
        bol_bands {dict} -- bollinger bands data object

    Returns:
        dict -- bollinger bands data object
    """
    # pylint: disable=too-many-branches
    period = kwargs.get('period', 20)
    bb_tabular_data = bol_bands['tabular']

    state = 'n'
    close = position['Close']
    for i in range(period, len(close)):

        if state == 'n':
            if close[i] < bb_tabular_data['middle_band'][i]:
                state = 'e1'
            elif close[i] > bb_tabular_data['middle_band'][i]:
                state = 'u1'

        elif state == 'e1':
            if close[i] <= bb_tabular_data['lower_band'][i]:
                state = 'e2'
                bol_bands['indicators'].append(
                    {'index': i, 'type': 'bearish', 'style': 'lower band crossover'})
            if close[i] > bb_tabular_data['middle_band'][i]:
                state = 'u1'

        elif state == 'e2':
            if close[i] <= bb_tabular_data['lower_band'][i]:
                bol_bands['indicators'].append(
                    {'index': i, 'type': 'bearish', 'style': 'lower band extreme'})
            else:
                state = 'e3'

        elif state == 'e3':
            if close[i] >= bb_tabular_data['middle_band'][i]:
                state = 'u1'

        elif state == 'u1':
            if close[i] >= bb_tabular_data['upper_band'][i]:
                state = 'u2'
                bol_bands['indicators'].append(
                    {'index': i, 'type': 'bullish', 'style': 'upper band crossover'})
            if close[i] < bb_tabular_data['middle_band'][i]:
                state = 'e1'

        elif state == 'u2':
            if close[i] >= bb_tabular_data['upper_band'][i]:
                bol_bands['indicators'].append(
                    {'index': i, 'type': 'bullish', 'style': 'upper band extreme'})
            else:
                state = 'u3'

        elif state == 'u3':
            if close[i] <= bb_tabular_data['middle_band'][i]:
                state = 'e1'

    return bol_bands


def find_m_shape_top(position: pd.DataFrame, bol_bands: dict, period: int) -> list:
    """Find the 'M' shape top

    Arguments:
        position {pd.DataFrame} -- fund dataset
        bol_bands {dict} -- bollinger bands data object
        period {int} -- look back period for bollinger band

    Returns:
        list -- list of 'M' detected tops
    """
    # pylint: disable=too-many-branches,too-many-statements
    m_list = []
    bb_tabular_data = bol_bands['tabular']

    state = 'n'
    prices = [0.0, 0.0, 0.0]
    close = position['Close']
    for i in range(period, len(close)):

        if (state == 'n') and (close[i] > bb_tabular_data['upper_band'][i]):
            state = 'w1'
            prices[0] = close[i]

        elif state == 'w1':
            if close[i] > prices[0]:
                prices[0] = close[i]
            else:
                state = 'w2'

        elif state == 'w2':
            if close[i] <= bb_tabular_data['middle_band'][i]:
                prices[1] = close[i]
                state = 'w3'
            elif close[i] > prices[0]:
                prices[0] = close[i]
                state = 'w1'

        elif state == 'w3':
            if close[i] < prices[1]:
                prices[1] = close[i]
            else:
                state = 'w4'

        elif state == 'w4':
            if close[i] > prices[0]:
                prices[2] = close[i]
                state = 'w5'
            elif close[i] >= bb_tabular_data['upper_band'][i]:
                state = 'w1'
            elif close[i] < prices[1]:
                prices[1] = close[i]
                state = 'w3'

        elif state == 'w5':
            if close[i] > prices[2]:
                prices[2] = close[i]
                if close[i] >= bb_tabular_data['upper_band'][i]:
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
                if close[i] >= bb_tabular_data['upper_band'][i]:
                    state = 'w1'

    return m_list
