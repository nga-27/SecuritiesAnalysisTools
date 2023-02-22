""" know sure thing """
import os

import pandas as pd
import numpy as np

from libs.utils import INDEXES, PlotType, generate_plot
from libs.features import normalize_signals

from .rate_of_change import roc_signal
from .moving_average import simple_moving_avg, exponential_moving_avg


def know_sure_thing(fund: pd.DataFrame, **kwargs) -> dict:
    """Know Sure Thing Oscillator

    Also known as the "summed rate of change" oscillator.

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- kst data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar = kwargs.get('progress_bar')

    kst = {}

    signal, signal_line = kst_signal(
        fund, plot_output=plot_output, name=name, views=views, p_bar=p_bar)

    kst['tabular'] = {'signal': signal, 'signal_line': signal_line}

    kst = kst_indicators(fund, kst)
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    kst = kst_metrics(fund, kst, plot_output=plot_output,
                      name=name, views=views)
    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    kst['length_of_data'] = len(kst['tabular']['signal'])
    kst['type'] = 'oscillator'

    return kst


def kst_signal(fund: pd.DataFrame, **kwargs) -> list:
    """Know Sure Thing - Signal

    Also known as the "Summed Rate of Change" Oscillator

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        periods {list} -- ROC periods (default: {[10, 15, 20, 30]})
        sma_intervals {list} -- sma intervals corresponding to the ROC periods
                                (default: {[10, 10, 10, 15]})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- kst signal and its 9d sma signal line
    """
    # pylint: disable=too-many-locals
    periods = kwargs.get('periods', [10, 15, 20, 30])
    sma_intervals = kwargs.get('sma_intervals', [10, 10, 10, 15])
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar = kwargs.get('p_bar')

    increment = 0.7 / float(len(periods) * 3)
    signal = [0.0] * len(fund['Close'])

    for i, period in enumerate(periods):
        roc = roc_signal(fund, period)
        if p_bar:
            p_bar.uptick(increment=increment)

        sma = simple_moving_avg(roc, sma_intervals[i], data_type='list')
        if p_bar:
            p_bar.uptick(increment=increment)

        for j, sig in enumerate(signal):
            sig += float(i + 1) * sma[j]
        if p_bar:
            p_bar.uptick(increment=increment)

    signal_line = simple_moving_avg(signal, 9, data_type='list')
    if p_bar:
        p_bar.uptick(increment=0.1)

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Know Sure Thing"

    generate_plot(
        PlotType.DUAL_PLOTTING, fund['Close'], **dict(
            y_list_2=[signal, signal_line], y1_label='Price', y2_label='KST', title=title,
            plot_output=plot_output, filename=os.path.join(name, views, f"kst_oscillator_{name}")
        )
    )

    return signal, signal_line


def kst_indicators(fund: pd.DataFrame, kst_dict: dict, **kwargs) -> dict:
    """KST Indicators

    Signal indicators for buy/sell

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        kst_dict {dict} -- kst data object

    Optional Args:
        upper_thresh {float} -- percentile for overbought (default: {85.0})
        lower_thresh {float} -- percentile for oversold (default: {15.0})

    Returns:
        dict -- kst data object
    """
    # pylint: disable=too-many-branches
    upper_thresh = kwargs.get('upper_thresh', 85.0)
    lower_thresh = kwargs.get('lower_thresh', 15.0)

    signal = kst_dict['tabular']['signal']
    line = kst_dict['tabular']['signal_line']

    upper_limit = np.percentile(signal, upper_thresh)
    lower_limit = np.percentile(signal, lower_thresh)

    state = 'n'
    signals = []
    for i, sig in enumerate(signal):
        date = fund.index[i].strftime("%Y-%m-%d")
        data = None

        if state == 'n':
            if sig > upper_limit:
                state = 'u'
            elif sig < lower_limit:
                state = 'l'

        elif state == 'u':
            if sig < upper_limit:
                state = 'n'
            else:
                if sig < line[i]:
                    state = 'n'
                    data = {
                        "type": 'bearish',
                        "value": 'overbought signal_line crossed',
                        "index": i,
                        "date": date
                    }

        elif state == 'l':
            if sig > lower_limit:
                state = 'n'
            else:
                if sig > line[i]:
                    state = 'n'
                    data = {
                        "type": 'bullish',
                        "value": 'oversold signal_line crossed',
                        "index": i,
                        "date": date
                    }

        if data is not None:
            signals.append(data)

    state = 'n'
    for i, sig in enumerate(signal):
        date = fund.index[i].strftime("%Y-%m-%d")
        data = None

        if state == 'n':
            if sig > line[i]:
                state = 'u'
            else:
                state = 'l'

        elif state == 'u':
            if sig < line[i]:
                state = 'l'
                data = {
                    "type": 'bearish',
                    "value": 'signal_line crossover',
                    "index": i,
                    "date": date
                }

        elif state == 'l':
            if sig > line[i]:
                state = 'u'
                data = {
                    "type": 'bullish',
                    "value": 'signal_line crossover',
                    "index": i,
                    "date": date
                }

        if data is not None:
            signals.append(data)

    kst_dict['signals'] = signals

    return kst_dict


def kst_metrics(fund: pd.DataFrame, kst_dict: dict, **kwargs) -> dict:
    """KST Metrics

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        kst_dict {dict} -- kst data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        views {str} -- (default: {''})

    Returns:
        dict -- kst data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')

    metrics = [0.0] * len(kst_dict['tabular']['signal'])

    for sig in kst_dict['signals']:
        if sig['type'] == 'bullish':
            multiply = 1.0
        else:
            multiply = -1.0

        if 'crossover' in sig['value']:
            metrics[sig['index']] += 0.2 * multiply

        if 'crossed' in sig['value']:
            metrics[sig['index']] += 1.0 * multiply

    metrics = exponential_moving_avg(metrics, 7, data_type='list')
    metrics = normalize_signals([metrics])[0]

    kst_dict['metrics'] = metrics

    name2 = INDEXES.get(name, name)
    title = f"{name2} - KST Metrics"

    generate_plot(
        PlotType.DUAL_PLOTTING, fund['Close'], **dict(
            y_list_2=kst_dict['metrics'], y1_label='Price', y2_label='Metrics', title=title,
            plot_output=plot_output, filename=os.path.join(name, views, f"kst_metrics_{name}")
        )
    )

    return kst_dict
