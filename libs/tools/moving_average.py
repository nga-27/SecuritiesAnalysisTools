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
    progress_bar = kwargs.get('progress_bar', None)

    tshort = []
    tmed = []
    tlong = []

    tot_len = len(fund['Close'])

    for i in range(config[0]):
        tshort.append(fund['Close'][i])
        tmed.append(fund['Close'][i])
        tlong.append(fund['Close'][i])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.05)

    for i in range(config[0], config[1]):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(fund['Close'][i])
        tlong.append(fund['Close'][i])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    for i in range(config[1], config[2]):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(np.mean(fund['Close'][i-config[1]:i+1]))
        tlong.append(fund['Close'][i])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.25)

    for i in range(config[2], tot_len):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(np.mean(fund['Close'][i-config[1]:i+1]))
        tlong.append(np.mean(fund['Close'][i-config[2]:i+1]))
    if progress_bar is not None:
        progress_bar.uptick(increment=0.5)

    name3 = SP500.get(name, name)
    name2 = name3 + \
        ' - Simple Moving Averages [{}, {}, {}]'.format(
            config[0], config[1], config[2])
    legend = ['Price', f'{config[0]}-SMA',
              f'{config[1]}-SMA', f'{config[2]}-SMA']
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
    function = kwargs.get('function', 'ema')
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    config = kwargs.get('config', [])
    progress_bar = kwargs.get('progress_bar', None)

    swings = []
    if function == 'sma':
        if config == []:
            sh, me, ln = triple_moving_average(
                fund, plot_output=False, name=name)
        else:
            sh, me, ln = triple_moving_average(
                fund, config=config, plot_output=False, name=name)
    else:
        if config == []:
            sh, me, ln = triple_exp_mov_average(
                fund, plot_output=False, name=name)
        else:
            sh, me, ln = triple_exp_mov_average(
                fund, config=config, plot_output=False, name=name)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.5)

    prev_state = 3
    hold = 'none'
    pb = int(len(sh) / 4)
    pb = [pb * (i+1) - 2 for i in range(4)]
    for i in range(len(sh)):
        state, hold = state_management(
            fund['Close'][i], sh[i], me[i], ln[i], prev_state, hold=hold)
        if state == 1:
            # Bullish Reversal
            swings.append(-2.0)
        elif state == 5:
            # Bearish Reversal
            swings.append(2.0)
        elif state == 7:
            swings.append(-1.0)
        elif state == 8:
            swings.append(1.0)
        elif state == 2:
            swings.append(0.5)
        elif state == 4:
            swings.append(-0.5)
        else:
            swings.append(0.0)
        prev_state = state
        if i in pb:
            if progress_bar is not None:
                progress_bar.uptick(increment=0.1)

    name3 = SP500.get(name, name)
    name2 = name3 + ' - Swing Trade EMAs'
    legend = ['Price', 'Short-EMA', 'Medium-EMA', 'Long-EMA', 'Swing Signal']
    if plot_output:
        specialty_plotting([fund['Close'], sh, me, ln, swings], alt_ax_index=[
                           4], legend=legend, title=name2)
    else:
        filename = name + '/swing_trades_ema_{}.png'.format(name)
        specialty_plotting([fund['Close'], sh, me, ln, swings], alt_ax_index=[4], legend=[
                           'Swing Signal'], title=name2, saveFig=True, filename=filename)

    mast = dict()
    mast['tabular'] = {}
    mast['tabular']['short'] = sh
    mast['tabular']['medium'] = me
    mast['tabular']['long'] = ln
    mast['tabular']['swing'] = swings

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    return mast


def state_management(price: float, sht: float, med: float, lng: float, prev_state: int, hold='bull'):
    """ 
    states: bullish -> bearish; 
        0 - price > sht > med > lng (bullish)
        1 - sht > med > lng & prev_state = 2 (bullish reversal)
        2 - sht < med > lng (potential bearish start)
        3 - "other"
        4 - sht > med < lng (potential bullish start)
        5 - sht < med < lng & prev_state = 4 (bearish reversal)
        6 - price < sht < med < lng (bearish)
        ======
        7 - enter into bullish from non-full bullish
        8 - enter into bearish from non-full bearish
    """
    if ((sht > med) and (med > lng) and (prev_state == 2)):
        state = 1
    elif ((sht < med) and (med < lng) and (prev_state == 4)):
        state = 5
    elif ((sht < med) and (med > lng)):
        #hold = 'none'
        state = 2
    elif ((sht > med) and (med < lng)):
        #hold = 'none'
        state = 4
    elif ((price < sht) and (sht < med) and (med < lng) and (prev_state != 8) and (hold != 'bear')):
        hold = 'bear'
        state = 8
    elif ((price > sht) and (sht > med) and (med > lng) and (prev_state != 7) and (hold != 'bull')):
        hold = 'bull'
        state = 7
    elif ((price > sht) and (sht > med) and (med > lng)):
        hold = 'bull'
        state = 0
    elif ((price < sht) and (sht < med) and (med < lng)):
        hold = 'bear'
        state = 6
    else:
        hold = 'none'
        state = 3

    return state, hold
