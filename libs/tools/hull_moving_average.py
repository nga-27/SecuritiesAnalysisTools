""" hull moving average """
import os

import pandas as pd
import numpy as np

from libs.utils import INDEXES, PlotType, generate_plot
from libs.features import normalize_signals

from .moving_averages_lib.weighted_moving_avg import weighted_moving_avg
from .moving_averages_lib.simple_moving_avg import simple_moving_avg


def hull_moving_average(position: pd.DataFrame, **kwargs) -> dict:
    """Hull Moving Average

    A Hull Moving Average (HMA) is a specific blend of several weighted moving averages
    (WMAs) within a WMA. This was created by Alan Hull.

    Formula:
    HMA = WMA(2 * WMA(closes, period=n/2) - WMA(closes, period=n), period=sqrt(n))

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- directory of plots (default: {''})

    Returns:
        dict -- hull ma data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')
    view = kwargs.get('view', '')

    hull = generate_hull_signal(
        position, plot_output=plot_output, name=name, p_bar=p_bar, view=view)

    hull = generate_swing_signal(position, hull, p_bar=p_bar)
    hull = swing_trade_metrics(
        position, hull, plot_output=plot_output, name=name, p_bar=p_bar, view=view)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    hull['type'] = 'trend'

    return hull


def generate_hull_signal(position: pd.DataFrame, **kwargs) -> list:
    """Generate Hull Signal

    Similar to triple moving average, this produces 3 period hull signals

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        period {list} -- list of ints for 3 lookback periods (default: {9, 16, 36})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})
        view {str} -- directory of plots (default: {''})

    Returns:
        list -- hull data object
    """
    # pylint: disable=too-many-locals
    period = kwargs.get('period', [9, 16, 36])
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('p_bar')
    view = kwargs.get('view', '')

    hull = {
        'short': {},
        'medium': {},
        'long': {},
        'tabular': {}
    }

    hull['short'] = {'period': period[0]}
    hull['medium'] = {'period': period[1]}
    hull['long'] = {'period': period[2]}

    plots = []
    for per in period:
        n_div_2 = weighted_moving_avg(position, int(per/2))
        n_ma = weighted_moving_avg(position, per)

        wma = []
        for i, div in enumerate(n_div_2):
            t_val = (2.0 * div) - n_ma[i]
            wma.append(t_val)

        sq_period = int(np.round(np.sqrt(float(per)), 0))
        hma = weighted_moving_avg(wma, sq_period, data_type='list')
        plots.append(hma.copy())

        if p_bar is not None:
            p_bar.uptick(increment=0.1)

    hull['tabular'] = {
        'short': plots[0],
        'medium': plots[1],
        'long': plots[2]
    }

    name3 = INDEXES.get(name, name)
    name2 = name3 + ' - Hull Moving Averages'
    legend = ['Price', 'HMA-short', 'HMA-medium', 'HMA-long']

    generate_plot(
        PlotType.GENERIC_PLOTTING, [position['Close'], plots[0], plots[1], plots[2]], **{
            "legend": legend, "title": name2, "plot_output": plot_output,
            "filename": os.path.join(name, view, f"hull_moving_average_{name}.png")
        }
    )

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    return hull


def generate_swing_signal(position: pd.DataFrame, swings: dict, **kwargs) -> dict:
    """Generate Swing Trade Signal

    u3 = sh > md > ln
    u2 = sh > (md && ln)
    u1 = sh > (md || ln)
    e3 = sh < md < ln
    e2 = sh < (md && ln)
    e1 = sh < (md || ln)
    n = "else"

    Transitions:
        n -> u2 = 0.5
        u2 -> u3 = 1.0
        n -> e2 = -0.5
        e2 -> e3 = -1.0

    Arguments:
        position {pd.DataFrame} -- fund dataset
        swings {dict} -- swing trade data object

    Optional Args:
        p_bar {ProgressBar} -- (default: {None})
        config {list} -- list of moving average lookback periods (default: {[9, 16, 36]})

    Returns:
        dict -- swing trade data object
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    p_bar = kwargs.get('p_bar')
    config = kwargs.get('config', [9, 16, 36])

    max_period = kwargs.get('max_period', 36)
    short = swings['tabular']['short']
    med = swings['tabular']['medium']
    long = swings['tabular']['long']

    close = position['Close']
    states = ['n'] * len(close)
    for i in range(max_period, len(states)):

        if (short[i] > med[i]) and (med[i] > long[i]):
            states[i] = 'u3'
        elif (short[i] > med[i]) and (short[i] > long[i]):
            states[i] = 'u2'
        elif (short[i] > med[i]) or (short[i] > long[i]):
            states[i] = 'u1'
        elif (short[i] < med[i]) and (med[i] < long[i]):
            states[i] = 'e3'
        elif (short[i] < med[i]) and (short[i] < long[i]):
            states[i] = 'e2'
        elif (short[i] < med[i]) or (short[i] < long[i]):
            states[i] = 'e1'

    periods = ''
    if config is not None:
        periods = f"{config[0]}-{config[1]}-{config[2]}"

    # Search for transitions
    features = []
    signal = [0.0] * len(states)
    set_block = 'n'
    for i in range(1, len(signal)):
        date = position.index[i].strftime("%Y-%m-%d")
        data = None

        if states[i] == 'u2':
            if (states[i-1] == 'e3') or (states[i-1] == 'e2') or (states[i-1] == 'e1'):
                signal[i] = 0.5
                set_block = 'u1'
                data = {
                    "type": 'bullish',
                    "value": f'swing crossover ({periods})',
                    "index": i,
                    "date": date
                }

        elif (states[i] == 'u3') and (states[i] != states[i-1]) and (set_block != 'u'):
            signal[i] = 1.0
            set_block = 'u'
            data = {
                "type": 'bullish',
                "value": f'confirmed bull trend ({periods})',
                "index": i,
                "date": date
            }

        elif close[i] > long[i]:
            signal[i] = 0.1

        elif states[i] == 'e2':
            if (states[i-1] == 'u3') or (states[i-1] == 'u2') or (states[i-1] == 'u1'):
                set_block = 'e1'
                signal[i] = -0.5
                data = {
                    "type": 'bearish',
                    "value": f'swing crossover ({periods})',
                    "index": i,
                    "date": date
                }

        elif (states[i] == 'e3') and (states[i] != states[i-1]) and (set_block != 'e'):
            set_block = 'e'
            signal[i] = -1.0
            data = {
                "type": 'bearish',
                "value": f'confirmed bear trend ({periods})',
                "index": i,
                "date": date
            }

        elif close[i] < long[i]:
            signal[i] = -0.1

        if data is not None:
            features.append(data)

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    swings['tabular']['swing'] = signal
    swings['length_of_data'] = len(swings['tabular']['swing'])
    swings['signals'] = features

    return swings


def swing_trade_metrics(position: pd.DataFrame, swings: dict, **kwargs) -> dict:
    """Swing Trade Metrics

    Arguments:
        position {pd.DataFrame} -- fund dataset
        swings {dict} -- hull data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})
        view {str} -- directory of plots (default: {''})

    Returns:
        dict -- hull data object
    """
    # pylint: disable=too-many-locals
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('p_bar')
    view = kwargs.get('view')

    weights = [1.0, 0.55, 0.25, 0.1]

    # Convert features to a "tabular" array
    tot_len = len(position['Close'])
    metrics = [0.0] * tot_len

    for i, val in enumerate(swings['tabular']['swing']):

        metrics[i] += val * weights[0]

        # Smooth the curves
        if i - 1 >= 0:
            metrics[i-1] += val * weights[1]
        if i + 1 < tot_len:
            metrics[i+1] += val * weights[1]
        if i - 2 >= 0:
            metrics[i-2] += val * weights[2]
        if i + 2 < tot_len:
            metrics[i+2] += val * weights[2]
        if i - 3 >= 0:
            metrics[i-3] += val * weights[3]
        if i + 3 < tot_len:
            metrics[i+3] += val * weights[3]

    norm_signal = normalize_signals([metrics])[0]
    metrics = simple_moving_avg(norm_signal, 7, data_type='list')
    swings['metrics'] = {'metrics': metrics}

    tshort = swings['tabular']['short']
    tmed = swings['tabular']['medium']
    tlong = swings['tabular']['long']

    mshort = []
    mmed = []
    mlong = []

    for i, close in enumerate(position['Close']):
        mshort.append(np.round((close - tshort[i]) / tshort[i] * 100.0, 3))
        mmed.append(np.round((close - tmed[i]) / tmed[i] * 100.0, 3))
        mlong.append(np.round((close - tlong[i]) / tlong[i] * 100.0, 3))

    shp = swings['short']['period']
    mdp = swings['medium']['period']
    lgp = swings['long']['period']

    swings['metrics'][f'{shp}-d'] = mshort
    swings['metrics'][f'{mdp}-d'] = mmed
    swings['metrics'][f'{lgp}-d'] = mlong

    name3 = INDEXES.get(name, name)
    name2 = name3 + ' - Hull Moving Average Metrics'

    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **{
            "y_list_2": swings['metrics']['metrics'], "y1_label": 'Price', "y2_label": 'Metrics',
            "title": name2, "plot_output": plot_output,
            "filename": os.path.join(name, view, f"hull_metrics_{name}.png")
        }
    )

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    return swings
