import pandas as pd
import numpy as np

from libs.utils import ProgressBar, dual_plotting, generic_plotting, bar_chart
from libs.utils import dates_extractor_list
from .moving_average import simple_moving_avg, exponential_moving_avg


def awesome_oscillator(position: pd.DataFrame, **kwargs) -> dict:
    """Awesome Oscillator

    Arguments:
        position {pd.DataFrame} -- fund data

    Optional Args:
        name {list} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        awesome_oscillator {dict} -- contains all ao information
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar = kwargs.get('progress_bar')

    ao = dict()

    signal = get_ao_signal(position, plot_output=plot_output,
                           name=name, progress_bar=progress_bar)

    # TODO: signal can be averaged over time (long-term trend); NORMALIZE signal

    if progress_bar is not None:
        progress_bar.uptick(increment=1.0)
    return ao


def get_ao_signal(position: pd.DataFrame, **kwargs) -> list:

    short_period = kwargs.get('short_period', 5)
    long_period = kwargs.get('long_period', 34)
    filter_style = kwargs.get('filter_style', 'sma')
    plot_output = kwargs.get('plot_output', True)
    p_bar = kwargs.get('progress_bar')
    name = kwargs.get('name', '')

    signal = []
    mid_points = []
    for i, high in enumerate(position['High']):
        mid = (high + position['Low'][i]) / 2
        mid_points.append(mid)

    if filter_style == 'sma':
        short_signal = simple_moving_avg(
            mid_points, short_period, data_type='list')
        long_signal = simple_moving_avg(
            mid_points, long_period, data_type='list')
    elif filter_style == 'ema':
        short_signal = exponential_moving_avg(
            mid_points, short_period, data_type='list')
        long_signal = exponential_moving_avg(
            mid_points, long_period, data_type='list')
    else:
        short_signal = []
        long_signal = []

    for i in range(long_period):
        signal.append(0.0)
    for i in range(long_period, len(long_signal)):
        diff = short_signal[i] - long_signal[i]
        signal.append(diff)

    med_term = simple_moving_avg(signal, 14, data_type='list')
    long_term = simple_moving_avg(signal, long_period, data_type='list')
    signal, med_term, long_term = normalize_signals(
        [signal, med_term, long_term])
    triggers = ao_signal_trigger(signal, med_term, long_term)
    x = dates_extractor_list(position)
    name2 = name + ' - Awesome Oscillator'

    if plot_output:
        dual_plotting(position['Close'], signal, 'Price', 'Awesome')
        dual_plotting([signal, med_term, long_term], position['Close'], [
                      'Awesome', 'Medium', 'Long'], 'Price')
        dual_plotting([signal, triggers], position['Close'], [
                      'Awesome', 'Triggers'], 'Price')
        bar_chart(signal, position=position, x=x, title=name2)
    else:
        filename = name + '/awesome_bar_{}'.format(name)
        bar_chart(signal, position=position, x=x,
                  saveFig=True, filename=filename, title=name2)

    return signal


def ao_signal_trigger(signal: list, medium: list, longer: list) -> list:
    trigger = []
    for i, sig in enumerate(signal):
        if (sig > 0.0) and (medium[i] > 0.0) and (longer[i] > 0.0):
            if (sig > medium[i]) and (medium[i] > longer[i]):
                trigger.append(1.0)
            else:
                trigger.append(0.0)
        elif (sig < 0.0) and (medium[i] < 0.0) and (longer[i] < 0.0):
            if (sig < medium[i]) and (medium[i] < longer[i]):
                trigger.append(-1.0)
            else:
                trigger.append(0.0)
        else:
            trigger.append(0.0)

    return trigger


def normalize_signals(signals: list) -> list:
    max_ = 0.0
    for sig in signals:
        m = np.max(np.abs(sig))
        if m > max_:
            max_ = m
    for i in range(len(signals)):
        new_sig = []
        for pt in signals[i]:
            pt2 = pt / max_
            new_sig.append(pt2)
        signals[i] = new_sig.copy()

    return signals
