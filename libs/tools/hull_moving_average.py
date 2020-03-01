import pandas as pd
import numpy as np

from libs.utils import ProgressBar
from libs.utils import generic_plotting, dual_plotting
from libs.features import normalize_signals
from .moving_average import weighted_moving_avg, simple_moving_avg


def hull_moving_average(position: pd.DataFrame, **kwargs) -> dict:
    """Hull Moving Average

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- hull ma data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')

    hull = generate_hull_signal(
        position, plot_output=plot_output, name=name, p_bar=p_bar)

    if p_bar is not None:
        p_bar.uptick(increment=1.0)

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

    Returns:
        list -- hull data object
    """
    period = kwargs.get('period', [9, 16, 36])
    plot_output = kwargs.get('plot_output', True)

    hull = {'short': {}, 'medium': {},
            'long': {}, 'tabular': {}}
    hull['short'] = {'period': period[0]}
    hull['medium'] = {'period': period[1]}
    hull['long'] = {'period': period[2]}

    plots = []
    for per in period:
        n_div_2 = weighted_moving_avg(position, int(per/2))
        n = weighted_moving_avg(position, per)

        wma = []
        for i, d in enumerate(n_div_2):
            t = (2.0 * d) - n[i]
            wma.append(t)

        sq_period = int(np.round(np.sqrt(float(per)), 0))
        hma = weighted_moving_avg(wma, sq_period, data_type='list')
        plots.append(hma.copy())

    hull['tabular'] = {'short': plots[0], 'medium': plots[1], 'long': plots[2]}
    hull = generate_swing_signal(position, hull)
    hull = swing_trade_metrics(position, hull)

    if plot_output:
        legend = ['Price', 'HMA-short', 'HMA-medium', 'HMA-long']
        generic_plotting([position['Close'], plots[0], plots[1],
                          plots[2]], legend=legend, title='Hull Moving Average')
        dual_plotting(position['Close'], hull['metrics'],
                      'Price', 'Metrics', title='Hull MA Metrics')

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
        max_period {int} -- longest term for triple moving average (default: {18})

    Returns:
        dict -- swing trade data object
    """

    max_period = kwargs.get('max_period', 36)
    sh = swings['tabular']['short']
    md = swings['tabular']['medium']
    ln = swings['tabular']['long']

    close = position['Close']
    states = ['n'] * len(close)
    for i in range(max_period, len(states)):

        if (sh[i] > md[i]) and (md[i] > ln[i]):
            states[i] = 'u3'
        elif (sh[i] > md[i]) and (sh[i] > ln[i]):
            states[i] = 'u2'
        elif (sh[i] > md[i]) or (sh[i] > ln[i]):
            states[i] = 'u1'
        elif (sh[i] < md[i]) and (md[i] < ln[i]):
            states[i] = 'e3'
        elif (sh[i] < md[i]) and (sh[i] < ln[i]):
            states[i] = 'e2'
        elif (sh[i] < md[i]) or (sh[i] < ln[i]):
            states[i] = 'e1'

    # Search for transitions
    signal = [0.0] * len(states)
    for i in range(1, len(signal)):
        if (states[i] == 'u2'):
            if (states[i-1] == 'e3') or (states[i-1] == 'e2') or (states[i-1] == 'e1'):
                signal[i] = 0.5

        elif (states[i] == 'u3') and (states[i] != states[i-1]):
            signal[i] = 1.0

        elif close[i] > ln[i]:
            signal[i] = 0.1

        elif (states[i] == 'e2'):
            if (states[i-1] == 'u3') or (states[i-1] == 'u2') or (states[i-1] == 'u1'):
                signal[i] = -0.5

        elif (states[i] == 'e3') and (states[i] != states[i-1]):
            signal[i] = -1.0

        elif close[i] < ln[i]:
            signal[i] = -0.1

    swings['tabular']['swing'] = signal
    return swings


def swing_trade_metrics(position: pd.DataFrame, swings: dict, **kwargs) -> dict:

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
    swings['metrics'] = simple_moving_avg(norm_signal, 7, data_type='list')

    return swings
