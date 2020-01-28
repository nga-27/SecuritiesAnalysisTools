import pprint
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

    ao['tabular'] = signal
    ao['features'] = ao_feature_detection(signal, position=position)

    integrator_differentiator(ao['features'], position, plot_output)

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

    signal, med_term, long_term = ao_normalize_signals(
        [signal, med_term, long_term])

    triggers = ao_signal_trigger(signal, med_term, long_term)
    x = dates_extractor_list(position)
    name2 = name + ' - Awesome Oscillator'

    if plot_output:
        dual_plotting([signal, med_term, long_term], position['Close'], [
                      'Awesome', 'Medium', 'Long'], 'Price')
        dual_plotting([signal, triggers], position['Close'], [
                      'Awesome', 'Triggers'], 'Price')
        bar_chart(signal, position=position, x=x, title=name2, bar_delta=True)
    else:
        filename = name + '/awesome_bar_{}'.format(name)
        bar_chart(signal, position=position, x=x,
                  saveFig=True, filename=filename, title=name2, bar_delta=True)

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


def ao_normalize_signals(signals: list) -> list:
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


def ao_feature_detection(signal: list, position: pd.DataFrame = None) -> list:
    features = []

    # Zero-crossover feature detection
    is_positive = signal[0] > 0.0
    for i, sig in enumerate(signal):
        if is_positive and (sig < 0.0):
            feat = {'index': i, 'feature': 'zero crossover', 'type': 'bearish'}
            features.append(feat)
            is_positive = False
        if (not is_positive) and (sig > 0.0):
            feat = {'index': i, 'feature': 'zero crossover', 'type': 'bullish'}
            features.append(feat)
            is_positive = True

    # "Twin Peaks" feature detection
    tpd = twin_peaks_detection(signal)
    for t in tpd:
        features.append(t)

    # "Saucer" feature detection
    saucer = saucer_detection(signal)
    for s in saucer:
        features.append(s)

    features.sort(key=lambda x: x['index'])

    return features


def twin_peaks_detection(signal: list) -> list:
    tpd = []

    is_positive = signal[0] > 0.0
    min_ = 1.0
    max_ = -1.0

    if is_positive:
        state = 'rise'
    else:
        state = 'drop'

    for i in range(1, len(signal)):
        if state == 'rise':
            # Rising, looking for first peak
            if signal[i] < signal[i-1]:
                # Found, now heading down dip
                max_ = signal[i-1]
                state = 'pos_saddle'
            continue

        elif state == 'pos_saddle':
            # First saddle, must stay above 0.  If dips, reset to negative start
            if signal[i] < 0.0:
                state = 'drop'
            else:
                if signal[i] > signal[i-1]:
                    # End of saddle, begin rise again
                    state = 'rise_2'
            continue

        elif state == 'rise_2':
            if signal[i] < max_:
                if signal[i] < signal[i-1]:
                    # Condition found!
                    state = 'bear_peaks'
                    tp = {'index': i, 'feature': 'twin peaks', 'type': 'bearish'}
                    tpd.append(tp)
            else:
                max_ = signal[i]
                state = 'rise'
            continue

        elif state == 'bear_peaks':
            if signal[i] < 0.0:
                state = 'drop'
            continue

        if state == 'drop':
            if signal[i] > signal[i-1]:
                min_ = signal[i-1]
                state = 'neg_saddle'
            continue

        elif state == 'neg_saddle':
            if signal[i] > 0.0:
                state = 'rise'
            else:
                if signal[i] < signal[i-1]:
                    state = 'drop_2'
            continue

        elif state == 'drop_2':
            if signal[i] > min_:
                if signal[i] > signal[i-1]:
                    state = 'bull_peaks'
                    tp = {'index': i, 'feature': 'twin peaks', 'type': 'bullish'}
                    tpd.append(tp)
            else:
                min_ = signal[i]
                state = 'drop'
            continue

        elif state == 'bull_peaks':
            if signal[i] > 0.0:
                state = 'rise'
            continue

    return tpd


def saucer_detection(signal: list) -> list:
    sd = []
    if signal[0] > 0.0:
        state = 'pos'
    else:
        state = 'neg'

    for i in range(1, len(signal)):
        if state == 'pos':
            if signal[i] < 0.0:
                state = 'neg'
            elif signal[i] < signal[i-1]:
                state = 'drop_1'
            continue

        elif state == 'drop_1':
            if signal[i] < 0.0:
                state = 'neg'
            elif signal[i] < signal[i-1]:
                state = 'drop_2'
            else:
                state = 'pos'
            continue

        elif state == 'drop_2':
            if signal[i] < 0.0:
                state = 'neg'
            elif signal[i] > signal[i-1]:
                state = 'pos'
                s = {'index': i, 'feature': 'saucer', 'type': 'bullish'}
                sd.append(s)
            continue

        elif state == 'neg':
            if signal[i] > 0.0:
                state = 'pos'
            elif signal[i] > signal[i-1]:
                state = 'rise_1'
            continue

        elif state == 'rise_1':
            if signal[i] > 0.0:
                state = 'pos'
            elif signal[i] > signal[i-1]:
                state = 'rise_2'
            else:
                state = 'neg'
            continue

        elif state == 'rise_2':
            if signal[i] > 0.0:
                state = 'pos'
            elif signal[i] < signal[i-1]:
                state = 'neg'
                s = {'index': i, 'feature': 'saucer', 'type': 'bearish'}
                sd.append(s)
            continue

    return sd


def integrator_differentiator(features: list, position: pd.DataFrame, plot_output: bool, name=''):
    key = int(max(position['Close']) / 20.0)

    plus_minus = []
    x_vals = []
    current_value = 0
    for feat in features:
        if feat['type'] == 'bullish':
            current_value += key
            plus_minus.append(current_value)
            x_vals.append(feat['index'])
        if feat['type'] == 'bearish':
            current_value -= key
            plus_minus.append(current_value)
            x_vals.append(feat['index'])

    pm_diff = [10 * key]
    for i in range(1, len(plus_minus)):
        if plus_minus[i] > plus_minus[i-1]:
            pm_diff.append(12 * key)
        elif plus_minus[i] < plus_minus[i-1]:
            pm_diff.append(8 * key)
        else:
            pm_diff.append(10 * key)

    if plot_output:
        generic_plotting([position['Close'], plus_minus, pm_diff], x=[
                         list(range(len(position))), x_vals, x_vals], title='Awesome Integrator / Differentiator',
                         legend=['Price', 'Integration', 'Differentiation'])
    else:
        filename = name + '/ao_diff_integ'
        generic_plotting([position['Close'], plus_minus, pm_diff], x=[
                         list(range(len(position))), x_vals, x_vals], title='Awesome Integrator / Differentiator',
                         legend=['Price', 'Integration', 'Differentiation'],
                         saveFig=True,
                         filename=filename)
