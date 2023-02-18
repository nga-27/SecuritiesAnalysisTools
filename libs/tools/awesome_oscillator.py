import os
import pandas as pd

from libs.utils import PlotType, generate_plot, dates_extractor_list
from libs.features import normalize_signals
from .moving_average import simple_moving_avg, exponential_moving_avg
from libs.utils import INDEXES


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
    view = kwargs.get('view', '')

    ao = dict()

    signal = get_ao_signal(position, plot_output=plot_output,
                           name=name, progress_bar=progress_bar, view=view)

    ao['tabular'] = signal
    ao['signals'] = ao_feature_detection(
        signal, position=position, progress_bar=progress_bar)

    plus_minus, x_index = integrator_differentiator(
        ao['signals'], position, plot_output)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    ao['pm'] = {'pm_data': plus_minus, 'indexes': x_index}

    ao = awesome_metrics(position, ao, plot_output=plot_output,
                         name=name, progress_bar=progress_bar, view=view)

    ao['length_of_data'] = len(ao['tabular'])
    ao['type'] = 'oscillator'

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)
    return ao


def get_ao_signal(position: pd.DataFrame, **kwargs) -> list:
    """Get Awesome Oscillator Signal

    Arguments:
        position {pd.DataFrame} -- dataset of fund

    Optional Args:
        short_period {int} -- moving average period (default: {5})
        long_period {int} -- moving average period (default: {34})
        filter_style {str} -- moving average type, 'sma' or 'ema' (default: {'sma'})
        plot_output {bool} -- True plots in realtime (default: {True})
        p_bar {ProgressBar} -- (default: {None})
        name {str} -- name of fund (default: {''})

    Returns:
        list -- awesome signal
    """
    short_period = kwargs.get('short_period', 5)
    long_period = kwargs.get('long_period', 34)
    filter_style = kwargs.get('filter_style', 'sma')
    plot_output = kwargs.get('plot_output', True)
    p_bar = kwargs.get('progress_bar')
    name = kwargs.get('name', '')
    view = kwargs.get('view')

    signal = []
    mid_points = []
    for i, high in enumerate(position['High']):
        mid = (high + position['Low'][i]) / 2
        mid_points.append(mid)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

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

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    for i in range(long_period):
        signal.append(0.0)
    for i in range(long_period, len(long_signal)):
        diff = short_signal[i] - long_signal[i]
        signal.append(diff)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    med_term = simple_moving_avg(signal, 14, data_type='list')
    long_term = simple_moving_avg(signal, long_period, data_type='list')

    signal, med_term, long_term = normalize_signals(
        [signal, med_term, long_term])

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    triggers = ao_signal_trigger(signal, med_term, long_term)

    x = dates_extractor_list(position)
    name3 = INDEXES.get(name, name)
    name2 = name3 + ' - Awesome Oscillator'

    generate_plot(
        PlotType.BAR_CHART, signal, **dict(
            position=position, x=x, save_fig=True, title=name2, bar_delta=True,
            plot_output=plot_output, filename=os.path.join(name, view, f"awesome_bar_{name}")
        )
    )
    if plot_output:
        generate_plot(
            PlotType.DUAL_PLOTTING, [signal, med_term, long_term], y_list_2=position['Close'],
            y1_label=['Awesome', 'Medium', 'Long'], y2_label='Price', plot_output=plot_output
        )
        generate_plot(
            PlotType.DUAL_PLOTTING, [signal, triggers], y_list_2=position['Close'],
            y1_label=['Awesome', 'Triggers'], y2_label='Price', plot_output=plot_output
        )
        # bar_chart(signal, position=position, x=x, title=name2, bar_delta=True)

    # else:
    #     filename = os.path.join(name, view, f"awesome_bar_{name}")
    #     bar_chart(signal, position=position, x=x,
    #               save_fig=True, filename=filename, title=name2, bar_delta=True)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    return signal


def ao_signal_trigger(signal: list, medium: list, longer: list) -> list:
    """ Triggers of various signals (experimental) """
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


def ao_feature_detection(signal: list, position: pd.DataFrame = None, **kwargs) -> list:
    """Awesome Oscillator Feature Detection

    Arguments:
        signal {list} -- Awesome oscillator signal

    Keyword Arguments:
        position {pd.DataFrame} -- fund data (default: {None})

    Optional Args:
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- list of dictionaries describing features
    """
    p_bar = kwargs.get('progress_bar')

    features = []

    # Zero-crossover feature detection
    is_positive = signal[0] > 0.0
    for i, sig in enumerate(signal):
        if is_positive and (sig < 0.0):
            date = position.index[i].strftime("%Y-%m-%d")
            feat = {
                'index': i,
                'value': 'zero crossover',
                'type': 'bearish',
                "date": date
            }
            features.append(feat)
            is_positive = False
        if (not is_positive) and (sig > 0.0):
            date = position.index[i].strftime("%Y-%m-%d")
            feat = {
                'index': i,
                'value': 'zero crossover',
                'type': 'bullish',
                "date": date
            }
            features.append(feat)
            is_positive = True

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    # "Twin Peaks" feature detection
    tpd = twin_peaks_detection(signal, position)
    for t in tpd:
        features.append(t)

    # "Saucer" feature detection
    saucer = saucer_detection(signal, position)
    for s in saucer:
        features.append(s)

    features.sort(key=lambda x: x['index'])

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    return features


def twin_peaks_detection(signal: list, position: pd.DataFrame) -> list:
    """ Twin Peaks signal """
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
                    date = position.index[i].strftime("%Y-%m-%d")
                    tp = {
                        'index': i,
                        'value': 'twin peaks',
                        'type': 'bearish',
                        "date": date
                    }
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
                    date = position.index[i].strftime("%Y-%m-%d")
                    tp = {
                        'index': i,
                        'value': 'twin peaks',
                        'type': 'bullish',
                        "date": date
                    }
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


def saucer_detection(signal: list, position: pd.DataFrame) -> list:
    """ Saucer feature detection """
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
                date = position.index[i].strftime("%Y-%m-%d")
                s = {
                    'index': i,
                    'value': 'saucer',
                    'type': 'bullish',
                    "date": date
                }
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
                date = position.index[i].strftime("%Y-%m-%d")
                s = {
                    'index': i,
                    'value': 'saucer',
                    'type': 'bearish',
                    "date": date
                }
                sd.append(s)
            continue

    return sd


def integrator_differentiator(features: list, position: pd.DataFrame, plot_output: bool, name='') -> list:
    """ Integrator Differentiator (experimental) """
    base = int(max(position['Close']) / 20.0)

    plus_minus = []
    x_vals = []
    current_value = 0

    for feat in features:
        if feat['type'] == 'bullish':
            current_value += base
            plus_minus.append(current_value)
            x_vals.append(feat['index'])

        if feat['type'] == 'bearish':
            current_value -= base
            plus_minus.append(current_value)
            x_vals.append(feat['index'])

    pm_data = [0]
    for i in range(1, len(plus_minus)):
        if plus_minus[i] > plus_minus[i-1]:
            pm_data.append(1)
        elif plus_minus[i] < plus_minus[i-1]:
            pm_data.append(-1)
        else:
            pm_data.append(0)

    return pm_data, x_vals


def awesome_metrics(position: pd.DataFrame, ao_dict: dict, **kwargs) -> dict:
    """Awesome Oscillator Metrics 

    Combination of pure oscillator signal + weighted trigger signals

    Arguments:
        position {pd.DataFrame} -- fund
        ao_dict {dict} -- awesome oscillator dictionary

    Optional Args:
        plot_output {bool} -- plots in real time if True (default: {True})
        name {str} -- name of fund (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- ao_dict w/ updated keys and data
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')
    period_change = kwargs.get('period_change', 5)
    view = kwargs.get('view')

    weights = [1.0, 0.85, 0.5, 0.05]

    # Convert features to a "tabular" array
    tot_len = len(position['Close'])
    metrics = [0.0] * tot_len
    plus_minus = ao_dict.get('pm', {}).get('pm_data')
    indexes = ao_dict.get('pm', {}).get('indexes', [])

    for i, ind in enumerate(indexes):
        metrics[ind] += float(plus_minus[i])

        # Smooth the curves
        if ind - 1 >= 0:
            metrics[ind-1] += float(plus_minus[i]) * weights[1]
        if ind + 1 < tot_len:
            metrics[ind+1] += float(plus_minus[i]) * weights[1]
        if ind - 2 >= 0:
            metrics[ind-2] += float(plus_minus[i]) * weights[2]
        if ind + 2 < tot_len:
            metrics[ind+2] += float(plus_minus[i]) * weights[2]
        if ind - 3 >= 0:
            metrics[ind-3] += float(plus_minus[i]) * weights[3]
        if ind + 3 < tot_len:
            metrics[ind+3] += float(plus_minus[i]) * weights[3]

    metrics2 = exponential_moving_avg(metrics, 7, data_type='list')
    norm = normalize_signals([metrics2])
    metrics3 = norm[0]

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    ao_signal = ao_dict['tabular']

    metrics4 = []
    for i, met in enumerate(metrics3):
        metrics4.append(met + ao_signal[i])

    changes = []
    min_ = 1.0 - min(metrics4)
    for _ in range(period_change):
        changes.append(0.0)
    for i in range(period_change, len(metrics4)):
        c = (((metrics4[i] + min_) /
              (metrics4[i-period_change] + min_)) - min_) * 100.0
        changes.append(c)

    ao_dict['metrics'] = metrics4
    ao_dict['changes'] = changes

    title = 'Awesome Oscillator Metrics'
    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], y_list_2=metrics4, y1_label='Price',
        y2_label='Metrics', title=title, plot_output=plot_output,
        filename=os.path.join(name, view, f"awesome_metrics_{name}.png")
    )

    ao_dict.pop('pm')
    return ao_dict
