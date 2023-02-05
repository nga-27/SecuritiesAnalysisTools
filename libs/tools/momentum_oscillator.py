import os

import pandas as pd
import numpy as np

from libs.utils import INDEXES, generate_plot, PlotType
from libs.features import find_local_extrema, normalize_signals

from .moving_average import simple_moving_avg


def momentum_oscillator(position: pd.DataFrame, **kwargs) -> dict:
    """Momentum Oscillator

    Arguments:
        position {pd.DataFrame} -- fund data

    Optional Args:
        progress_bar {ProgressBar} -- (default: {None})
        plot_output {bool} -- (default: {True})
        name {str} -- {default: {''}}

    Returns:
        dict -- momentum object
    """
    progress_bar = kwargs.get('progress_bar')
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')

    mo = dict()

    mo['tabular'] = generate_momentum_signal(
        position, plot_output=plot_output, name=name, view=view)
    if progress_bar is not None:
        progress_bar.uptick(increment=0.3)

    # Check against signal line (9-day MA)
    mo['bear_bull'] = compare_against_signal_line(
        mo['tabular'], position=position, name=name, plot_output=plot_output)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    # Feature detection, primarily divergences (5% drop from peak1 then rise again to peak2?)
    mo['signals'] = mo_feature_detection(
        mo['tabular'], position, plot_output=plot_output, name=name)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.3)

    # Metrics creation like in awesome oscillator
    mo = momentum_metrics(
        position, mo, plot_output=plot_output, name=name, view=view)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    mo['type'] = 'oscillator'
    mo['length_of_data'] = len(mo['tabular'])

    return mo


def generate_momentum_signal(position: pd.DataFrame, **kwargs) -> list:
    """Generate Momentum Signal

    https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        interval {int} -- lookback period (default: {20})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})

    Returns:
        list -- momentum signal
    """
    interval = kwargs.get('interval', 20)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')

    signal = []
    for i in range(interval-1):
        signal.append(0.0)
    for i in range(interval-1, len(position['Close'])):
        sum_up = 0.0
        sum_down = 0.0
        for j in range(i-(interval-2), i):
            if position['Close'][j] > position['Close'][j-1]:
                sum_up += position['Close'][j] - position['Close'][j-1]
            else:
                sum_down += np.abs(position['Close']
                                   [j] - position['Close'][j-1])
        cmo = 100.0 * (sum_up - sum_down) / (sum_up + sum_down)
        signal.append(cmo)

    name2 = INDEXES.get(name, name)
    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **dict(
            y_list_2=signal, y1_label='Price', y2_label='CMO',
            title=f'{name2} - (Chande) Momentum Oscillator',
            filename=os.path.join(name, view, f"momentum_oscillator_{name}.png"),
        )
    )

    return signal


def compare_against_signal_line(signal: list, **kwargs) -> list:
    """Compare Against Signal Line

    Compare momentum oscillator signal vs. sma signal line

    Arguments:
        signal {list} -- momentum oscillator signal

    Optional Args:
        plot_output {bool} -- (default: {True})
        interval {int} -- lookback for simple moving average (default: {9})
        position {pd.DataFrame} -- fund dataset (default: {[]})

    Returns:
        list -- bear_bull oscillator signal
    """
    plot_output = kwargs.get('plot_output', True)
    interval = kwargs.get('interval', 9)
    position = kwargs.get('position', [])

    signal_line = simple_moving_avg(signal, interval, data_type='list')
    bear_bull = []
    for i in range(len(signal)):
        if signal[i] > signal_line[i]:
            bear_bull.append(1.0)
        elif signal[i] < signal_line[i]:
            bear_bull.append(-1.0)
        else:
            bear_bull.append(0.0)

    if plot_output and len(position) > 0:
        generate_plot(
            PlotType.DUAL_PLOTTING, position['Close'], **dict(
                y_list_2=bear_bull, y1_label='Price', y2_label='Bear_Bull', title='Bear Bull'
            )
        )

    return bear_bull


def mo_feature_detection(signal: list, position: pd.DataFrame, **kwargs) -> list:
    """MO Feature Detection

    Find various features associated with this oscillator

    Arguments:
        signal {list} -- momentum oscillator signal
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of feature dictionaries
    """
    price_extrema = find_local_extrema(position['Close'])
    signal_extrema = find_local_extrema(signal, threshold=0.40, points=True)

    # Compare extrema to find divergences!
    features = feature_matches(
        price_extrema, signal_extrema, position, signal)

    return features


def feature_matches(pos_extrema: list, mo_extrema: list,
                    position: pd.DataFrame, mo_signal: list, **kwargs) -> list:
    """Feature Matches

    Search for and match for various features associated with momentum oscillator

    Arguments:
        pos_extrema {list} -- price extrema list
        mo_extrema {list} -- momentum oscillator extrema list
        position {pd.DataFrame} -- fund dataset
        mo_signal {list} -- momentum oscillator signal

    Returns:
        list -- feature list of dictionaries
    """
    features = []
    closes = position['Close']

    # Look at mo_extrema vs closes
    maxes = list(filter(lambda x: x['type'] == 'max', mo_extrema))
    for i in range(1, len(maxes)):
        if maxes[i]['val'] < maxes[i-1]['val']:
            if closes[maxes[i]['index']] >= closes[maxes[i-1]['index']]:
                # Bearish divergence
                date = closes.index[maxes[i]['index']].strftime("%Y-%m-%d")
                obj = {
                    "index": maxes[i]['index'],
                    "type": 'bearish',
                    'value': 'divergence',
                    "date": date
                }
                features.append(obj)

    mins = list(filter(lambda x: x['type'] == 'min', mo_extrema))
    for i in range(1, len(mins)):
        if mins[i]['val'] > mins[i-1]['val']:
            if closes[mins[i]['index']] <= closes[mins[i-1]['index']]:
                # Bullish divergence
                date = closes.index[mins[i]['index']].strftime("%Y-%m-%d")
                obj = {
                    "index": mins[i]['index'],
                    "type": 'bullish',
                    'value': 'divergence',
                    "date": date
                }
                features.append(obj)

    return features


def momentum_metrics(position: pd.DataFrame, mo_dict: dict, **kwargs) -> dict:
    """Momentum Oscillator Metrics 

    Combination of pure oscillator signal + weighted features

    Arguments:
        position {pd.DataFrame} -- fund
        mo_dict {dict} -- momentum oscillator dict

    Optional Args:
        plot_output {bool} -- plots in real time if True (default: {True})
        name {str} -- name of fund (default: {''})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- (default: {''})

    Returns:
        dict -- mo_dict w/ updated keys and data
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    period_change = kwargs.get('period_change', 5)
    view = kwargs.get('view', '')

    weights = [1.3, 0.85, 0.55, 0.1]

    # Convert features to a "tabular" array
    tot_len = len(position['Close'])
    metrics = [0.0] * tot_len
    mo_features = mo_dict['signals']
    signal = mo_dict['tabular']

    for feat in mo_features:
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

    norm_signal = normalize_signals([signal])[0]

    metrics4 = []
    changes = []
    for i, met in enumerate(metrics):
        metrics4.append(met + norm_signal[i])

    min_ = np.abs(min(metrics4)) + 1.0
    for _ in range(period_change):
        changes.append(0.0)
    for i in range(period_change, len(metrics4)):
        c = (((metrics4[i] + min_) /
              (metrics4[i-period_change] + min_)) - 1.0) * 100.0
        changes.append(c)

    mo_dict['metrics'] = metrics4
    mo_dict['changes'] = changes

    title = '(Chande) Momentum Oscillator Metrics'
    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **dict(
            y_list_2=metrics4, y1_label='Price', y2_label='Metrics', title=title,
            plot_output=plot_output,
            filename=os.path.join(name, view, f"momentum_metrics_{name}.png")
        )
    )

    return mo_dict
