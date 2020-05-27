import os
import pandas as pd
import numpy as np

from libs.utils import dual_plotting, ProgressBar
from libs.utils import INDEXES
from .rate_of_change import roc_signal
from .moving_average import simple_moving_avg


def know_sure_thing(fund: pd.DataFrame, **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')
    p_bar = kwargs.get('progress_bar')

    kst = dict()
    signal, signal_line = kst_signal(
        fund, plot_output=plot_output, name=name, views=views)

    kst['tabular'] = {'signal': signal, 'signal_line': signal_line}

    kst = kst_indicators(fund, kst)

    kst = kst_metrics(fund, kst, plot_output=plot_output,
                      name=name, views=views)

    if p_bar is not None:
        p_bar.uptick(increment=1.0)

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

    Returns:
        list -- kst signal and its 9d sma signal line
    """
    periods = kwargs.get('periods', [10, 15, 20, 30])
    sma_intervals = kwargs.get('sma_intervals', [10, 10, 10, 15])
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    views = kwargs.get('views', '')

    signal = [0.0] * len(fund['Close'])

    for i, period in enumerate(periods):
        roc = roc_signal(fund, period)
        sma = simple_moving_avg(roc, sma_intervals[i], data_type='list')

        for j in range(len(signal)):
            signal[j] += float(i + 1) * sma[j]

    signal_line = simple_moving_avg(signal, 9, data_type='list')

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Know Sure Thing"

    if plot_output:
        dual_plotting(fund['Close'], [signal, signal_line],
                      'Price', 'KST', title=title)
    else:
        filename = os.path.join(name, views, f"kst_oscillator_{name}")
        dual_plotting(fund['Close'], [signal, signal_line], 'Price',
                      'KST', title=title, saveFig=True, filename=filename)

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
                    data = {
                        "type": 'bullish',
                        "value": 'oversold signal_line crossed',
                        "index": i,
                        "date": date
                    }

        if data is not None:
            signals.append(data)

    kst_dict['signals'] = signals

    return kst_dict


def kst_metrics(fund: pd.DataFrame, kst_dict: dict, **kwargs) -> dict:

    return kst_dict
