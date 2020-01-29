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

    if plot_output:
        dual_plotting(position['Close'], bear_bull,
                      'Price', 'Bear_Bull', title='Bear Bull')

    return bear_bull
