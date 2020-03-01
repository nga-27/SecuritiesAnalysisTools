import math
import pandas as pd
import numpy as np

from libs.utils import generic_plotting, specialty_plotting, SP500


def exponential_moving_avg(dataset, interval: int, **kwargs) -> list:
    """Exponential Moving Average

    Arguments:
        dataset -- tabular data, either list or pd.DataFrame
        interval {int} -- window to exponential moving average

    Optional Args:
        data_type {str} -- either 'DataFrame' or 'list' (default: {'DataFrame'})
        key {str} -- column key (if type 'DataFrame'); (default: {'Close'})

    Returns:
        list -- filtered data
    """
    data_type = kwargs.get('data_type', 'DataFrame')
    key = kwargs.get('key', 'Close')

    if data_type == 'DataFrame':
        data = list(dataset[key])
    else:
        data = dataset

    ema = []
    k = 2.0 / (float(interval) + 1.0)
    for i in range(interval-1):
        ema.append(data[i])
    for i in range(interval-1, len(data)):
        ema.append(np.mean(data[i-(interval-1):i+1]))
        if i != interval-1:
            ema[i] = ema[i-1] * (1.0 - k) + data[i] * k

    return ema


def windowed_moving_avg(dataset, interval: int, **kwargs) -> list:
    """Windowed Moving Average

    Arguments:
        dataset -- tabular data, either list or pd.DataFrame
        interval {int} -- window to windowed moving average

    Optional Args:
        data_type {str} -- either 'DataFrame' or 'list' (default: {'DataFrame'})
        key {str} -- column key (if type 'DataFrame'); (default: {'Close'})
        filter_type {str} -- either 'simple' or 'exponential' (default: {'simple'})
        weight_strength {float} -- numerator for ema weight (default: {2.0})

    Returns:
        list -- filtered data
    """
    data_type = kwargs.get('data_type', 'DataFrame')
    key = kwargs.get('key', 'Close')
    filter_type = kwargs.get('filter_type', 'simple')
    weight_strength = kwargs.get('weight_strength', 2.0)

    if data_type == 'DataFrame':
        data = list(dataset[key])
    else:
        data = dataset

    wma = []

    if filter_type == 'simple':
        left = int(np.floor(float(interval) / 2))
        if left == 0:
            return data
        for i in range(left):
            wma.append(data[i])
        for i in range(left, len(data)-left):
            wma.append(np.mean(data[i-(left):i+(left)]))
        for i in range(len(data)-left, len(data)):
            wma.append(data[i])

    elif filter_type == 'exponential':
        left = int(np.floor(float(interval) / 2))
        weight = weight_strength / (float(interval) + 1.0)
        if weight > 1.0:
            weight = 1.0
        for i in range(left):
            wma.append(data[i])
        for i in range(left, len(data)-left):
            sum_len = len(data[i-(left):i+(left)]) - 1
            sum_vals = np.sum(data[i-(left):i+(left)])
            sum_vals -= data[i]
            sum_vals = sum_vals / float(sum_len)
            sum_vals = data[i] * weight + sum_vals * (1.0 - weight)
            wma.append(sum_vals)
        for i in range(len(data)-left, len(data)):
            wma.append(data[i])

    return wma


def simple_moving_avg(dataset, interval: int, **kwargs) -> list:
    """Simple Moving Average

    Arguments:
        dataset -- tabular data, either list or pd.DataFrame
        interval {int} -- window to windowed moving average

    Optional Args:
        data_type {str} -- either 'DataFrame' or 'list' (default: {'DataFrame'})
        key {str} -- column key (if type 'DataFrame'); (default: {'Close'})

    Returns:
        list -- filtered data
    """
    data_type = kwargs.get('data_type', 'DataFrame')
    key = kwargs.get('key', 'Close')

    if data_type == 'DataFrame':
        data = list(dataset[key])
    else:
        data = dataset

    ma = []
    for i in range(interval-1):
        ma.append(data[i])
    for i in range(interval-1, len(data)):
        av = np.mean(data[i-(interval-1):i+1])
        ma.append(av)

    return ma


def weighted_moving_avg(dataset, interval: int, **kwargs) -> list:
    """Weighted Moving Average

    Arguments:
        dataset -- tabular data, either list or pd.DataFrame
        interval {int} -- window to windowed moving average

    Optional Args:
        data_type {str} -- either 'DataFrame' or 'list' (default: {'DataFrame'})
        key {str} -- column key (if type 'DataFrame'); (default: {'Close'})

    Returns:
        list -- filtered data
    """
    data_type = kwargs.get('data_type', 'DataFrame')
    key = kwargs.get('key', 'Close')

    if data_type == 'DataFrame':
        data = list(dataset[key])
    else:
        data = dataset

    wma = []
    for i in range(interval):
        wma.append(data[i])

    divisor = 0
    for i in range(interval):
        divisor += i+1

    for i in range(interval, len(data)):
        av = 0.0
        for j in range(interval):
            av += float(j+1) * data[i - (interval-1-j)]
        av = av / float(divisor)
        wma.append(av)

    return wma


def triple_moving_average(fund: pd.DataFrame, **kwargs) -> dict:
    """
    Triple Moving Avg:  3 simple moving averages of "config" length

    args:
        fund:           (pd.DataFrame) fund historical data

    optional args:
        name:           (list) name of fund, primarily for plotting; DEFAULT=''
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        config:         (list of ints) list of moving average time periods; DEFAULT=[12, 50, 200]
        progress_bar:   (ProgressBar) DEFAULT=None

    returns:
        tma:            (dict) contains all ma information in "short", "medium", and "long" keys
    """
    name = kwargs.get('name', '')
    config = kwargs.get('config', [12, 50, 200])
    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', False)
    progress_bar = kwargs.get('progress_bar', None)

    tshort = simple_moving_avg(fund, config[0])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    tmed = simple_moving_avg(fund, config[1])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    tlong = simple_moving_avg(fund, config[2])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    mshort = []
    mmed = []
    mlong = []
    for i, close in enumerate(fund['Close']):
        mshort.append(np.round((close - tshort[i]) / tshort[i] * 100.0, 3))
        mmed.append(np.round((close - tmed[i]) / tmed[i] * 100.0, 3))
        mlong.append(np.round((close - tlong[i]) / tlong[i] * 100.0, 3))

    triple_exp_mov_average(
        fund, config=[9, 21, 50], plot_output=plot_output, name=name)

    name3 = SP500.get(name, name)
    name2 = name3 + \
        ' - Simple Moving Averages [{}, {}, {}]'.format(
            config[0], config[1], config[2])
    legend = ['Price', f'{config[0]}-SMA',
              f'{config[1]}-SMA', f'{config[2]}-SMA']

    if not out_suppress:
        if plot_output:
            generic_plotting([fund['Close'], tshort, tmed, tlong],
                             legend=legend, title=name2)
        else:
            filename = name + '/simple_moving_averages_{}.png'.format(name)
            generic_plotting([fund['Close'], tshort, tmed, tlong],
                             legend=legend, title=name2, saveFig=True, filename=filename)

    tma = dict()
    tma['short'] = {'period': config[0]}
    tma['medium'] = {'period': config[1]}
    tma['long'] = {'period': config[2]}
    tma['tabular'] = {'short': tshort, 'medium': tmed, 'long': tlong}
    tma['metrics'] = {'short': mshort, 'medium': mmed, 'long': mlong}

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    return tma


def triple_exp_mov_average(fund: pd.DataFrame, config=[9, 13, 50], plot_output=True, name='') -> list:

    tshort = exponential_moving_avg(fund, config[0])
    tmed = exponential_moving_avg(fund, config[1])
    tlong = exponential_moving_avg(fund, config[2])

    name3 = SP500.get(name, name)
    name2 = name3 + \
        ' - Exp Moving Averages [{}, {}, {}]'.format(
            config[0], config[1], config[2])
    legend = ['Price', f'{config[0]}-EMA',
              f'{config[1]}-EMA', f'{config[2]}-EMA']
    if plot_output:
        generic_plotting([fund['Close'], tshort, tmed, tlong],
                         legend=legend, title=name2)
    else:
        filename = name + '/exp_moving_averages_{}.png'.format(name)
        generic_plotting([fund['Close'], tshort, tmed, tlong],
                         legend=legend, title=name2, saveFig=True, filename=filename)

    return tshort, tmed, tlong


def moving_average_swing_trade(fund: pd.DataFrame, **kwargs):
    """
    Triple Moving Avg:  3 simple moving averages of "config" length

    args:
        fund:           (pd.DataFrame) fund historical data

    optional args:
        function:       (str) type of filtering scheme; DEFAULT='ema'
        name:           (list) name of fund, primarily for plotting; DEFAULT=''
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        config:         (list of ints) list of moving average time periods; DEFAULT=[]
        progress_bar:   (ProgressBar) DEFAULT=None

    returns:
        mast:           (dict) contains all ma information in "short", "medium", "long", and "swing" keys
    """
    function = kwargs.get('function', 'sma')
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    config = kwargs.get('config', [4, 9, 18])
    progress_bar = kwargs.get('progress_bar', None)

    if plot_output:
        out_suppress = False
    else:
        out_suppress = True

    if function == 'sma':
        if config == []:
            tma = triple_moving_average(
                fund, plot_output=plot_output, name=name, out_suppress=out_suppress)
            sh = tma['tabular']['short']
            me = tma['tabular']['medium']
            ln = tma['tabular']['long']
        else:
            tma = triple_moving_average(
                fund, config=config, plot_output=plot_output, name=name, out_suppress=out_suppress)
            sh = tma['tabular']['short']
            me = tma['tabular']['medium']
            ln = tma['tabular']['long']
    else:
        if config == []:
            sh, me, ln = triple_exp_mov_average(
                fund, plot_output=plot_output, name=name)
        else:
            sh, me, ln = triple_exp_mov_average(
                fund, config=config, plot_output=plot_output, name=name)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    mast = dict()
    mast['tabular'] = {}
    mast['tabular']['short'] = sh
    mast['tabular']['medium'] = me
    mast['tabular']['long'] = ln

    mast = generate_swing_signal(fund, mast, max_period=config[2])
    mast = swing_trade_metrics(fund, mast)

    swings = mast['metrics']

    if progress_bar is not None:
        progress_bar.uptick(increment=0.3)

    name3 = SP500.get(name, name)
    name2 = name3 + ' - Swing Trade SMAs'
    legend = ['Price', 'Short-SMA', 'Medium-SMA', 'Long-SMA', 'Swing Signal']
    if plot_output:
        specialty_plotting([fund['Close'], sh, me, ln, swings], alt_ax_index=[
                           4], legend=legend, title=name2)
    else:
        filename = name + '/swing_trades_sma_{}.png'.format(name)
        specialty_plotting([fund['Close'], sh, me, ln, swings], alt_ax_index=[4], legend=[
                           'Swing Signal'], title=name2, saveFig=True, filename=filename)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.5)

    return mast


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

    max_period = kwargs.get('max_period', 18)
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

    norm_signal = normalize_signals_local([metrics])[0]
    swings['metrics'] = simple_moving_avg(norm_signal, 7, data_type='list')

    return swings


def normalize_signals_local(signals: list) -> list:
    max_ = 0.0
    for sig in signals:
        m = np.max(np.abs(sig))
        if m > max_:
            max_ = m

    if max_ != 0.0:
        for i in range(len(signals)):
            new_sig = []
            for pt in signals[i]:
                pt2 = pt / max_
                new_sig.append(pt2)
            signals[i] = new_sig.copy()

    return signals
