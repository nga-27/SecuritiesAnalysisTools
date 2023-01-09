import os

import pandas as pd
import numpy as np

from libs.utils import specialty_plotting, candlestick_plot, INDEXES


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
    if interval < len(data) - 3:
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

    if interval < len(data) - 3:
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
    if interval < len(data) - 3:
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


def typical_price_signal(data: pd.DataFrame) -> list:
    """Typical Price Signal

    Generate the typical price calculation (close + high + low) / 3

    Arguments:
        data {pd.DataFrame} -- dataframe dataset

    Returns:
        list -- typical price signal
    """
    tps = []
    for i, close in enumerate(data['Close']):
        summed = close + data['Low'][i] + data['High'][i]
        summed /= 3.0
        tps.append(summed)

    return tps


###################################################################


def triple_moving_average(fund: pd.DataFrame, **kwargs) -> dict:
    """Triple Moving Average

    3 simple moving averages of "config" length

    Arguments:
        fund {pd.DataFrame} -- fund historical data

    Optional Args:
        name {list} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        config {list of ints} -- list of moving average time periods (default: {[12, 50, 200]})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- directory of plots (default: {''})

    Returns:
        tma {dict} -- contains all ma information in "short", "medium", and "long" keys
    """
    name = kwargs.get('name', '')
    config = kwargs.get('config', [12, 50, 200])
    plot_output = kwargs.get('plot_output', True)
    out_suppress = kwargs.get('out_suppress', False)
    progress_bar = kwargs.get('progress_bar', None)
    view = kwargs.get('view', '')

    sma_short = simple_moving_avg(fund, config[0])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    sma_med = simple_moving_avg(fund, config[1])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    sma_long = simple_moving_avg(fund, config[2])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    triple_exp_mov_average(
        fund, config=[9, 21, 50], plot_output=plot_output, name=name, view=view)

    mshort = []
    mmed = []
    mlong = []
    tshort_x = []
    tmed_x = []
    tlong_x = []
    tshort2 = []
    tmed2 = []
    tlong2 = []

    if len(sma_short) > 0:
        for i, close in enumerate(fund['Close']):
            mshort.append(np.round((close - sma_short[i]) / sma_short[i] * 100.0, 3))
        tshort_x, tshort2 = adjust_signals(fund, sma_short, offset=config[0])

    if len(sma_med) > 0:
        for i, close in enumerate(fund['Close']):
            mmed.append(np.round((close - sma_med[i]) / sma_med[i] * 100.0, 3))
        tmed_x, tmed2 = adjust_signals(fund, sma_med, offset=config[1])

    if len(sma_long) > 0:
        for i, close in enumerate(fund['Close']):
            mlong.append(np.round((close - sma_long[i]) / sma_long[i] * 100.0, 3))
        tlong_x, tlong2 = adjust_signals(fund, sma_long, offset=config[2])

    plot_short = {"plot": tshort2, "color": "blue",
                  "legend": f"{config[0]}-day MA", "x": tshort_x}
    plot_med = {"plot": tmed2, "color": "orange",
                "legend": f"{config[1]}-day MA", "x": tmed_x}
    plot_long = {"plot": tlong2,
                 "color": "black", "legend": f"{config[2]}-day MA", "x": tlong_x}

    if not out_suppress:
        name3 = INDEXES.get(name, name)
        name2 = name3 + \
            ' - Simple Moving Averages [{}, {}, {}]'.format(
                config[0], config[1], config[2])

        if plot_output:
            candlestick_plot(fund, title=name2, additional_plts=[plot_short, plot_med, plot_long])

        else:
            filename = os.path.join(name, view, f"simple_moving_averages_{name}.png")
            candlestick_plot(fund, title=name2, filename=filename,
                             saveFig=True, additional_plts=[plot_short, plot_med, plot_long])

    tma = dict()
    tma['short'] = {'period': config[0]}
    tma['medium'] = {'period': config[1]}
    tma['long'] = {'period': config[2]}
    tma['tabular'] = {'short': sma_short, 'medium': sma_med, 'long': sma_long}
    tma['metrics'] = {f'{config[0]}-d': mshort,
                      f'{config[1]}-d': mmed, f'{config[2]}-d': mlong}

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    tma['type'] = 'trend'
    tma['length_of_data'] = len(tma['tabular']['short'])
    tma['signals'] = find_crossovers(tma, fund)

    return tma


def triple_exp_mov_average(fund: pd.DataFrame, config=[9, 20, 50], **kwargs) -> list:
    """Triple Exponential Moving Average

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {str})
        view {str} -- file directory of plots (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Keyword Arguments:
        config {list} -- look back period (default: {[9, 13, 50]})

    Returns:
        list -- plots and signals
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    p_bar = kwargs.get('progress_bar')
    out_suppress = kwargs.get('out_suppress', False)

    tema = dict()

    tshort = exponential_moving_avg(fund, config[0])
    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    tmed = exponential_moving_avg(fund, config[1])
    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    tlong = exponential_moving_avg(fund, config[2])
    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    tema['tabular'] = {'short': tshort, 'medium': tmed, 'long': tlong}
    tema['short'] = {"period": config[0]}
    tema['medium'] = {"period": config[1]}
    tema['long'] = {"period": config[2]}

    tshort_x, tshort2 = adjust_signals(fund, tshort, offset=config[0])
    tmed_x, tmed2 = adjust_signals(fund, tmed, offset=config[1])
    tlong_x, tlong2 = adjust_signals(fund, tlong, offset=config[2])

    plot_short = {"plot": tshort2, "color": "blue",
                  "legend": f"{config[0]}-day MA", "x": tshort_x}
    plot_med = {"plot": tmed2, "color": "orange",
                "legend": f"{config[1]}-day MA", "x": tmed_x}
    plot_long = {"plot": tlong2,
                 "color": "black", "legend": f"{config[2]}-day MA", "x": tlong_x}

    mshort = []
    mmed = []
    mlong = []

    for i, close in enumerate(fund['Close']):
        mshort.append(np.round((close - tshort[i]) / tshort[i] * 100.0, 3))
        mmed.append(np.round((close - tmed[i]) / tmed[i] * 100.0, 3))
        mlong.append(np.round((close - tlong[i]) / tlong[i] * 100.0, 3))

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    tema['metrics'] = {f'{config[0]}-d': mshort,
                       f'{config[1]}-d': mmed, f'{config[2]}-d': mlong}

    if not out_suppress:
        name3 = INDEXES.get(name, name)
        name2 = name3 + \
            ' - Exp Moving Averages [{}, {}, {}]'.format(
                config[0], config[1], config[2])
        # legend = ['Price', f'{config[0]}-EMA',
        #           f'{config[1]}-EMA', f'{config[2]}-EMA']

        # plots = [fund['Close'], tshort2, tmed2, tlong2]
        # x_vals = [fund.index, tshort_x, tmed_x, tlong_x]

        if plot_output:
            candlestick_plot(fund, title=name2, additional_plts=[
                             plot_short, plot_med, plot_long])
            # generic_plotting(plots, x=x_vals,
            #                  legend=legend, title=name2)

        else:
            filename = os.path.join(
                name, view, f"exp_moving_averages_{name}.png")
            candlestick_plot(fund, title=name2, filename=filename,
                             saveFig=True, additional_plts=[plot_short, plot_med, plot_long])
            # generic_plotting(plots, x=x_vals,
            #                  legend=legend, title=name2, saveFig=True, filename=filename)

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    tema['type'] = 'trend'
    tema['length_of_data'] = len(tema['tabular']['short'])
    tema['signals'] = find_crossovers(tema, fund)

    return tema


def moving_average_swing_trade(fund: pd.DataFrame, **kwargs):
    """Triple Moving Average

    3 simple moving averages of "config" length

    Arguments:
        fund {pd.DataFrame} -- fund historical data

    Optional Args:
        function {str} -- type of filtering scheme (default: {'sma'})
        name {str} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        config {list} -- list of moving average time periods (default: {[4, 9, 18]})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- directory for plot (default: {''})

    Returns:
        mast {dict} -- contains all ma information in "short", "medium", "long", and "swing" keys
    """
    function = kwargs.get('function', 'sma')
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    config = kwargs.get('config', [4, 9, 18])
    progress_bar = kwargs.get('progress_bar', None)
    view = kwargs.get('view', '')

    if plot_output:
        out_suppress = False
    else:
        out_suppress = True

    if function == 'sma':
        if config == []:
            tma = triple_moving_average(
                fund, plot_output=plot_output, name=name,
                out_suppress=out_suppress, view=view)
        else:
            tma = triple_moving_average(
                fund, config=config, plot_output=plot_output,
                name=name, out_suppress=out_suppress, view=view)
        sh = tma['tabular']['short']
        me = tma['tabular']['medium']
        ln = tma['tabular']['long']

    elif function == 'ema':
        if config == []:
            tma = triple_exp_mov_average(
                fund, plot_output=plot_output, name=name,
                out_suppress=out_suppress, view=view)
        else:
            tma = triple_exp_mov_average(
                fund, config=config, plot_output=plot_output,
                name=name, out_suppress=out_suppress, view=view)
        sh = tma['tabular']['short']
        me = tma['tabular']['medium']
        ln = tma['tabular']['long']

    else:
        return {}

    if progress_bar is not None:
        progress_bar.uptick(increment=0.4)

    mast = dict()
    mast['tabular'] = {}
    mast['tabular']['short'] = sh
    mast['tabular']['medium'] = me
    mast['tabular']['long'] = ln

    mast = generate_swing_signal(
        fund, mast, max_period=config[2], config=config)
    mast = swing_trade_metrics(fund, mast)

    swings = mast['metrics']

    if progress_bar is not None:
        progress_bar.uptick(increment=0.4)

    name3 = INDEXES.get(name, name)
    funct_name = function.upper()
    name2 = name3 + f' - Swing Trade {funct_name}s'
    legend = ['Price', 'Short-SMA', 'Medium-SMA', 'Long-SMA', 'Swing Signal']

    if plot_output:
        specialty_plotting([fund['Close'], sh, me, ln, swings], alt_ax_index=[
                           4], legend=legend, title=name2)
    else:
        filename = os.path.join(
            name, view, f"swing_trades_{function}_{name}.png")
        specialty_plotting([fund['Close'], sh, me, ln, swings], alt_ax_index=[4], legend=[
                           'Swing Signal'], title=name2, saveFig=True, filename=filename)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    mast['type'] = 'oscillator'

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
        config {list} -- list of moving average lookback periods (default: {None})

    Returns:
        dict -- swing trade data object
    """
    max_period = kwargs.get('max_period', 18)
    config = kwargs.get('config')

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

    periods = ''
    if config is not None:
        periods = f"{config[0]}-{config[1]}-{config[2]}"

    # Search for transitions
    features = []
    signal = [0.0] * len(states)
    set_block = 'n'
    for i in range(1, len(signal)):
        date = position.index[i].strftime("%Y-%m-%d")
        data = None

        if (states[i] == 'u2'):
            if (states[i-1] == 'e3') or (states[i-1] == 'e2') or (states[i-1] == 'e1'):
                signal[i] = 0.5
                set_block = 'u1'
                data = {
                    "type": 'bullish',
                    "value": f'swing crossover ({periods})',
                    "index": i,
                    "date": date
                }

        elif (states[i] == 'u3') and (states[i] != states[i-1]) and (set_block != 'u'):
            signal[i] = 1.0
            set_block = 'u'
            data = {
                "type": 'bullish',
                "value": f'confirmed bull trend ({periods})',
                "index": i,
                "date": date
            }

        elif close[i] > ln[i]:
            signal[i] = 0.1

        elif (states[i] == 'e2'):
            if (states[i-1] == 'u3') or (states[i-1] == 'u2') or (states[i-1] == 'u1'):
                set_block = 'e1'
                signal[i] = -0.5
                data = {
                    "type": 'bearish',
                    "value": f'swing crossover ({periods})',
                    "index": i,
                    "date": date
                }

        elif (states[i] == 'e3') and (states[i] != states[i-1]) and (set_block != 'e'):
            set_block = 'e'
            signal[i] = -1.0
            data = {
                "type": 'bearish',
                "value": f'confirmed bear trend ({periods})',
                "index": i,
                "date": date
            }

        elif close[i] < ln[i]:
            signal[i] = -0.1

        if data is not None:
            features.append(data)

    swings['tabular']['swing'] = signal
    swings['signals'] = features
    swings['length_of_data'] = len(swings['tabular']['swing'])

    return swings


def swing_trade_metrics(position: pd.DataFrame, swings: dict, **kwargs) -> dict:
    """Swing Trade Metrics

    Standard 1.0 to -1.0 metrics

    Arguments:
        position {pd.DataFrame} -- fund dataset
        swings {dict} -- swing trade data object

    Returns:
        dict -- swing trade data object
    """
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
    """ Normalize local signals based off max """
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


def find_crossovers(mov_avg: dict, position: pd.DataFrame) -> list:
    """Find Crossovers

    Find crossovers in signals, particularly with a short/medium/long average

    Arguments:
        mov_avg {dict} -- triple moving average data object
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of crossover event dictionaries
    """
    tshort = mov_avg['tabular']["short"]
    tmed = mov_avg['tabular']["medium"]
    tlong = mov_avg['tabular']["long"]

    sh_period = mov_avg['short']['period']
    md_period = mov_avg['medium']['period']
    ln_period = mov_avg['long']['period']

    features = []

    if len(tshort) == 0 or len(tmed) == 0 or len(tlong) == 0:
        return features

    state = 'at'
    for i, sh in enumerate(tshort):
        data = None
        date = position.index[i].strftime("%Y-%m-%d")

        if state == 'at':
            if sh > tmed[i]:
                state = 'above'
                data = {
                    "type": 'bullish',
                    "value": f'golden crossover (midterm: {sh_period}d > {md_period}d)',
                    "index": i,
                    "date": date
                }
            elif sh < tmed[i]:
                state = 'below'
                data = {
                    "type": 'bearish',
                    "value": f'death crossover (midterm: {md_period}d > {sh_period}d)',
                    "index": i,
                    "date": date
                }

        elif state == 'above':
            if sh < tmed[i]:
                state = 'below'
                data = {
                    "type": 'bearish',
                    "value": f'death crossover (midterm: {md_period}d > {sh_period}d)',
                    "index": i,
                    "date": date
                }

        elif state == 'below':
            if sh > tmed[i]:
                state = 'above'
                data = {
                    "type": 'bullish',
                    "value": f'golden crossover (midterm: {sh_period}d > {md_period}d)',
                    "index": i,
                    "date": date
                }

        if data is not None:
            features.append(data)

    state = 'at'
    for i, md in enumerate(tmed):
        data = None
        date = position.index[i].strftime("%Y-%m-%d")

        if state == 'at':
            if md > tlong[i]:
                state = 'above'
                data = {
                    "type": 'bullish',
                    "value": f'golden crossover (longterm: {md_period}d > {ln_period}d)',
                    "index": i,
                    "date": date
                }
            elif md < tlong[i]:
                state = 'below'
                data = {
                    "type": 'bearish',
                    "value": f'death crossover (longterm: {ln_period}d > {md_period}d)',
                    "index": i,
                    "date": date
                }

        elif state == 'above':
            if md < tlong[i]:
                state = 'below'
                data = {
                    "type": 'bearish',
                    "value": f'death crossover (longterm: {ln_period}d > {md_period}d)',
                    "index": i,
                    "date": date
                }

        elif state == 'below':
            if md > tlong[i]:
                state = 'above'
                data = {
                    "type": 'bullish',
                    "value": f'golden crossover (longterm: {md_period}d > {ln_period}d)',
                    "index": i,
                    "date": date
                }

        if data is not None:
            features.append(data)

    return features


def adjust_signals(fund: pd.DataFrame, signal: list, offset=0) -> list:
    """Adjust Signals

    Arguments:
        fund {pd.DataFrame} -- fund dataset (with index as dates)
        signal {list} -- signal to adjust

    Keyword Arguments:
        offset {int} -- starting point (default: {0})

    Returns:
        list -- new adjusted x_plots, adjusted signal
    """
    x_values = []
    adj_signal = []
    for i in range(offset, len(signal)):
        x_values.append(fund.index[i])
        adj_signal.append(signal[i])

    return x_values, adj_signal
