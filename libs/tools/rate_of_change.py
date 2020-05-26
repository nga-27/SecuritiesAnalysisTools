import os
import pandas as pd
import numpy as np

from libs.utils import dual_plotting, generic_plotting
from libs.utils import INDEXES
from libs.utils import ProgressBar
from .moving_average import adjust_signals


def rate_of_change_oscillator(fund: pd.DataFrame, periods: list = [10, 20, 40], **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar = kwargs.get('progress_bar')

    roc = dict()

    tshort = roc_signal(fund, periods[0])
    tmed = roc_signal(fund, periods[1])
    tlong = roc_signal(fund, periods[2])

    roc['tabular'] = {'short': tshort, 'medium': tmed, 'long': tlong}
    roc['short'] = periods[0]
    roc['medium'] = periods[1]
    roc['long'] = periods[2]

    tsx, ts2 = adjust_signals(fund, tshort, offset=periods[0])
    tmx, tm2 = adjust_signals(fund, tmed, offset=periods[1])
    tlx, tl2 = adjust_signals(fund, tlong, offset=periods[2])

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Rate of Change Oscillator"
    plots = [ts2, tm2, tl2]
    xs = [tsx, tmx, tlx]

    if plot_output:
        dual_plotting(fund['Close'], [tshort, tmed, tlong],
                      'Price', 'Rate of Change', title=title,
                      legend=[f'ROC-{periods[0]}', f'ROC-{periods[1]}', f'ROC-{periods[2]}'])
        generic_plotting(plots, x=xs, title=title, legend=[
                         f'ROC-{periods[0]}', f'ROC-{periods[1]}', f'ROC-{periods[2]}'])

    else:
        filename = os.path.join(name, views, f"rate_of_change_{name}")
        dual_plotting(fund['Close'], [tshort, tmed, tlong],
                      'Price', 'Rate of Change', title=title,
                      legend=[f'ROC-{periods[0]}',
                              f'ROC-{periods[1]}', f'ROC-{periods[2]}'],
                      saveFig=True, filename=filename)

    roc = roc_metrics(fund, roc)

    if p_bar is not None:
        p_bar.uptick(increment=1.0)

    return roc


def roc_signal(fund: pd.DataFrame, interval: int) -> list:
    """Rate of Change Signal

    Generate the oscillator signal for rate of change.

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        interval {int} -- lookback period for comparison

    Returns:
        list -- ROC signal
    """
    signal = [0.0] * len(fund['Close'])
    for i in range(interval, len(signal)):
        signal[i] = ((fund['Close'][i] / fund['Close']
                      [i-interval]) - 1.0) * 100.0

    return signal


def roc_metrics(fund: pd.DataFrame, roc_dict: dict) -> dict:

    # Zero crossings
    # Oversold, Overbought -> derive thresholds on fly... 5, 95 percentile? +/- 10? for each roc
    # with thresholds, once leaving is signal
    # Signal weighting: 10d (0.65), 20d (1.0), 40d (0.4)
    MAP_TABULAR = {
        'short': 0.65,
        'medium': 1.0,
        'long': 0.4
    }

    metrics = [0.0] * len(fund['Close'])

    # Look at zero crossovers first
    for tab in roc_dict['tabular']:
        sh_state = 'n'
        multiple = MAP_TABULAR[tab]

        for i, sig in enumerate(roc_dict['tabular'][tab]):
            if sh_state == 'n':
                if sig < 0.0:
                    sh_state = 'down'
                elif sig > 0.0:
                    sh_state = 'up'

            elif sh_state == 'up':
                if sig < 0.0:
                    sh_state = 'down'
                    metrics[i] += -1.0 * multiple

            elif sh_state == 'down':
                if sig > 0.0:
                    sh_state = 'up'
                    metrics[i] += multiple

    roc_dict['metrics'] = metrics
    return roc_dict
