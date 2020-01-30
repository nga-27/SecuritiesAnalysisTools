import pandas as pd
import numpy as np

from libs.utils import ProgressBar
from libs.utils import dual_plotting
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

    features = []
    price_extrema = find_local_extrema(position['Close'])
    signal_extrema = find_local_extrema(signal, threshold=0.40, points=True)

    # Compare extrema to find divergences!

    return features


def find_local_extrema(position: list, threshold=0.03, points=False) -> list:
    features = []
    # Price divergence with signal
    max_val = 0.0
    max_ind = 0
    min_val = 0.0
    min_ind = 0
    trend = 'none'

    for i, close in enumerate(position):
        if trend == 'none':
            if close > max_val:
                max_val = close
                max_ind = i
                trend = 'up'
            else:
                min_val = close
                min_ind = i
                trend = 'down'
        elif trend == 'up':
            if points:
                denote = threshold * 100.0
            else:
                denote = max_val * threshold

            if close > max_val:
                max_val = close
                max_ind = i
            elif close < max_val - denote:
                obj = {"val": max_val, "index": max_ind, "type": "max"}
                print(obj)
                features.append(obj)
                trend = 'down'
                min_val = close
                min_ind = i
        elif trend == 'down':
            if points:
                denote = threshold * 100.0
            else:
                denote = min_val * threshold

            if close < min_val:
                min_val = close
                min_ind = i
            elif close > min_val + denote:
                obj = {"val": min_val, "index": min_ind, "type": "min"}
                print(obj)
                features.append(obj)
                trend = 'up'
                max_val = close
                max_ind = i

    return features
