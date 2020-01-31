from datetime import datetime
import pandas as pd
import numpy as np

from libs.utils import ProgressBar
from libs.utils import dual_plotting
from libs.features import find_local_extrema
from .moving_average import simple_moving_avg


def momentum_oscillator(position: pd.DataFrame, **kwargs) -> dict:

    progress_bar = kwargs.get('progress_bar')

    mo = dict()

    mo['tabular'] = generate_momentum_signal(position)

    # Check against signal line (9-day MA)
    mo['bear_bull'] = compare_against_signal_line(
        mo['tabular'], position=position)

    # Feature detection, primarily divergences (5% drop from peak1 then rise again to peak2?)
    mo['features'] = mo_feature_detection(mo['tabular'], position)

    dual_plotting(position['Close'], mo['tabular'], 'price', 'momentum')

    # Metrics creation like in awesome oscillator

    if progress_bar is not None:
        progress_bar.uptick(increment=1.0)

    return mo


def generate_momentum_signal(position: pd.DataFrame, **kwargs) -> list:
    # https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
    interval = kwargs.get('interval', 20)
    plot_output = kwargs.get('plot_output', True)

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

    if plot_output:
        dual_plotting(position['Close'], signal, 'Price',
                      'CMO', title='Momentum Oscillator')

    return signal


def compare_against_signal_line(signal: list, **kwargs) -> list:
    plot_output = kwargs.get('plot_output', False)
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

    if plot_output and (len(position) > 0):
        dual_plotting(position['Close'], bear_bull,
                      'Price', 'Bear_Bull', title='Bear Bull')

    return bear_bull


def mo_feature_detection(signal: list, position: pd.DataFrame, **kwargs) -> list:
    p_bar = kwargs.get('progress_bar')

    price_extrema = find_local_extrema(position['Close'])
    signal_extrema = find_local_extrema(signal, threshold=0.40, points=True)

    # Compare extrema to find divergences!
    features = feature_matches(
        price_extrema, signal_extrema, position, signal)

    return features


def feature_matches(pos_extrema: list, mo_extrema: list,
                    position: pd.DataFrame, mo_signal: list, **kwargs) -> list:
    features = []
    closes = position['Close']

    # Look at mo_extrema vs closes
    maxes = list(filter(lambda x: x['type'] == 'max', mo_extrema))
    for i in range(1, len(maxes)):
        if maxes[i]['val'] < maxes[i-1]['val']:
            if closes[maxes[i]['index']] >= closes[maxes[i-1]['index']]:
                # Bearish divergence
                date = closes.index[maxes[i]['index']].strftime("%Y-%m-%d")
                obj = {"index": maxes[i]['index'],
                       "type": 'bearish', 'category': 'divergence',
                       "date": date}
                features.append(obj)

    mins = list(filter(lambda x: x['type'] == 'min', mo_extrema))
    for i in range(1, len(mins)):
        if mins[i]['val'] > mins[i-1]['val']:
            if closes[mins[i]['index']] <= closes[mins[i-1]['index']]:
                # Bullish divergence
                date = closes.index[mins[i]['index']].strftime("%Y-%m-%d")
                obj = {"index": mins[i]['index'],
                       "type": 'bullish', 'category': 'divergence',
                       "date": date}
                features.append(obj)

    return features
