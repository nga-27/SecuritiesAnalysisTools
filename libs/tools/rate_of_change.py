""" rate of change """
import os
from typing import Union

import pandas as pd
import numpy as np

from libs.utils import INDEXES, generate_plot, PlotType
from libs.features import normalize_signals

from .moving_averages_lib.utils import adjust_signals
from .moving_averages_lib.exponential_moving_avg import exponential_moving_avg


def rate_of_change_oscillator(fund: pd.DataFrame,
                              periods: Union[list, None] = None, **kwargs) -> dict:
    """Rate of Change Oscillator

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        periods {list} -- lookback periods for ROC (default: {[10, 20, 40]})

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- roc data object
    """
    # pylint: disable=too-many-locals
    if not periods:
        periods = [10, 20, 40]

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar = kwargs.get('progress_bar')

    roc = {}
    t_short = roc_signal(fund, periods[0])
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    t_med = roc_signal(fund, periods[1])
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    t_long = roc_signal(fund, periods[2])
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    roc['tabular'] = {'short': t_short, 'medium': t_med, 'long': t_long}
    roc['short'] = periods[0]
    roc['medium'] = periods[1]
    roc['long'] = periods[2]

    tsx, ts2 = adjust_signals(fund, t_short, offset=periods[0])
    tmx, tm2 = adjust_signals(fund, t_med, offset=periods[1])
    tlx, tl2 = adjust_signals(fund, t_long, offset=periods[2])
    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Rate of Change Oscillator"
    plots = [ts2, tm2, tl2]
    x_s = [tsx, tmx, tlx]

    generate_plot(
        PlotType.DUAL_PLOTTING, fund['Close'], **{
            "y_list_2": [t_short, t_med, t_long], "y1_label": 'Price', "y2_label": 'Rate of Change',
            "title": title,
            "legend": [f'ROC-{periods[0]}', f'ROC-{periods[1]}', f'ROC-{periods[2]}'],
            "plot_output": plot_output,
            "filename": os.path.join(name, views, f"rate_of_change_{name}")
        }
    )

    generate_plot(
        PlotType.GENERIC_PLOTTING, plots, **{
            "x": x_s, "title": title,
            "legend": [f'ROC-{periods[0]}', f'ROC-{periods[1]}', f'ROC-{periods[2]}'],
            "plot_output": plot_output
        }
    )

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    roc = roc_metrics(fund, roc, plot_output=plot_output,
                      name=name, views=views, p_bar=p_bar)

    roc['length_of_data'] = len(roc['tabular']['short'])
    roc['type'] = 'oscillator'

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

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


def roc_metrics(fund: pd.DataFrame, roc_dict: dict, **kwargs) -> dict:
    """Rate of Change Metrics

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        roc_dict {dict} -- roc data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- roc data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar = kwargs.get('p_bar')

    map_tabular = {
        'short': 0.65,
        'medium': 1.0,
        'long': 0.4
    }

    roc_dict['metrics'] = [0.0] * len(fund['Close'])
    roc_dict['signals'] = []

    # Look at zero crossovers first
    roc_dict = roc_zero_crossovers(fund, roc_dict, map_tabular)
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    roc_dict = roc_over_threshold_crossovers(fund, roc_dict, map_tabular)
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    roc_dict['metrics'] = exponential_moving_avg(
        roc_dict['metrics'], 7, data_type='list')

    roc_dict['metrics'] = normalize_signals([roc_dict['metrics']])[0]
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Rate of Change Metrics"

    generate_plot(
        PlotType.DUAL_PLOTTING, fund['Close'], **{
            "y_list_2": roc_dict['metrics'], "y1_label": 'Price', "y2_label": 'ROC Metrics',
            "title": title,
            "plot_output": plot_output, "filename": os.path.join(name, views, f"roc_metrics_{name}")
        }
    )

    return roc_dict


def roc_zero_crossovers(fund: pd.DataFrame, roc_dict: dict, map_tabular: dict, **kwargs) -> dict:
    """Rate of Change Zero Crossovers

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        roc_dict {dict} -- roc data object
        MAP_TABULAR {dict} -- weightings per period signal

    Optional Args:
        weight {float} -- overall weighting of metric detection (default: {0.75})

    Returns:
        dict -- roc data object
    """
    # pylint: disable=too-many-locals
    weight = kwargs.get('weight', 0.75)

    tabular = roc_dict['tabular']
    metrics = roc_dict['metrics']
    signals = []

    for tab in tabular:
        sh_state = 'n'
        multiple = map_tabular[tab] * weight
        period = roc_dict[tab]

        for i, sig in enumerate(tabular[tab]):
            date = fund.index[i].strftime("%Y-%m-%d")
            data = None

            if sh_state == 'n':
                if sig < 0.0:
                    sh_state = 'down'
                elif sig > 0.0:
                    sh_state = 'up'

            elif sh_state == 'up':
                if sig < 0.0:
                    sh_state = 'down'
                    metrics[i] += -1.0 * multiple
                    data = {
                        "type": 'bearish',
                        "value": f'zero crossover {period}d',
                        "date": date,
                        "index": i
                    }

            elif sh_state == 'down':
                if sig > 0.0:
                    sh_state = 'up'
                    metrics[i] += multiple
                    data = {
                        "type": 'bullish',
                        "value": f'zero crossover {period}d',
                        "date": date,
                        "index": i
                    }

            if data is not None:
                signals.append(data)

    roc_dict['metrics'] = metrics
    roc_dict['signals'].extend(signals)

    return roc_dict


def roc_over_threshold_crossovers(fund: pd.DataFrame, roc_dict: dict,
                                  map_tabular: dict, **kwargs) -> dict:
    """Rate of Change: Over-Threshold Crossovers

    Dynamically determine thresholds, then find when roc signal enters/leaves zone. Trigger
    signal on leaving zone.

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        roc_dict {dict} -- roc data object
        MAP_TABULAR {dict} -- weightings per period signal

    Optional Args:
        top_thresh {float} -- percentile for overbought zone (default: {90.0})
        bottom_thresh {float} -- percentile for oversold zone (default: {10.0})
        weight {float} -- weight of specific metric

    Returns:
        dict -- roc data object
    """
    # pylint: disable=too-many-locals
    top_thresh = kwargs.get('top_thresh', 90.0)
    bottom_thresh = kwargs.get('bottom_thresh', 10.0)
    weight = kwargs.get('weight', 1.0)

    metrics = roc_dict['metrics']
    tabular = roc_dict['tabular']
    signals = []

    for tab in tabular:
        over_top = np.percentile(tabular[tab], top_thresh)
        over_bottom = np.percentile(tabular[tab], bottom_thresh)

        state = 'n'
        multiple = map_tabular[tab] * weight
        period = roc_dict[tab]

        for i, sig in enumerate(tabular[tab]):
            date = fund.index[i].strftime("%Y-%m-%d")
            data = None

            if state == 'n':
                if sig > over_top:
                    state = 'u'
                if sig < over_bottom:
                    state = 'd'

            elif state == 'u':
                if sig < over_top:
                    state = 'n'
                    metrics[i] += -1.0 * multiple
                    data = {
                        "type": 'bearish',
                        "value": f'overbought crossover {period}d',
                        "date": date,
                        "index": i
                    }

            elif state == 'd':
                if sig > over_bottom:
                    state = 'n'
                    metrics[i] += multiple
                    data = {
                        "type": 'bullish',
                        "value": f'oversold crossover {period}d',
                        "date": date,
                        "index": i
                    }

            if data is not None:
                signals.append(data)

    roc_dict['metrics'] = metrics
    roc_dict['signals'].extend(signals)

    return roc_dict
