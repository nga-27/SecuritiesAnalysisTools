""" moving averages (exponential, simple, windowed) """
import os
from typing import Union

import pandas as pd
import numpy as np

from libs.utils import INDEXES, PlotType, generate_plot
from .moving_averages_lib.utils import adjust_signals, find_crossovers, normalize_signals_local
from .moving_averages_lib.exponential_moving_avg import exponential_moving_avg
from .moving_averages_lib.simple_moving_avg import simple_moving_avg


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
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
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

    triple_exp_mov_average(fund, config=[9, 21, 50], plot_output=plot_output, name=name, view=view)

    m_short = []
    m_med = []
    m_long = []
    t_short_x = []
    t_med_x = []
    t_long_x = []
    t_short2 = []
    t_med2 = []
    t_long2 = []

    if len(sma_short) > 0:
        for i, close in enumerate(fund['Close']):
            m_short.append(np.round((close - sma_short[i]) / sma_short[i] * 100.0, 3))
        t_short_x, t_short2 = adjust_signals(fund, sma_short, offset=config[0])

    if len(sma_med) > 0:
        for i, close in enumerate(fund['Close']):
            m_med.append(np.round((close - sma_med[i]) / sma_med[i] * 100.0, 3))
        t_med_x, t_med2 = adjust_signals(fund, sma_med, offset=config[1])

    if len(sma_long) > 0:
        for i, close in enumerate(fund['Close']):
            m_long.append(np.round((close - sma_long[i]) / sma_long[i] * 100.0, 3))
        t_long_x, t_long2 = adjust_signals(fund, sma_long, offset=config[2])

    plot_short = {
        "plot": t_short2,
        "color": "blue",
        "legend": f"{config[0]}-day MA",
        "x": t_short_x
    }
    plot_med = {
        "plot": t_med2,
        "color": "orange",
        "legend": f"{config[1]}-day MA",
        "x": t_med_x
    }
    plot_long = {
        "plot": t_long2,
        "color": "black",
        "legend": f"{config[2]}-day MA",
        "x": t_long_x
    }

    if not out_suppress:
        name3 = INDEXES.get(name, name)
        name2 = name3 + f' - Simple Moving Averages [{config[0]}, {config[1]}, {config[2]}]'

        generate_plot(
            PlotType.CANDLESTICKS, fund, **{
                "title": name2, "plot_output": plot_output, "save_fig": True,
                "additional_plots": [plot_short, plot_med, plot_long],
                "filename": os.path.join(name, view, f"simple_moving_averages_{name}.png")
            }
        )

    tma = {}
    tma['short'] = {'period': config[0]}
    tma['medium'] = {'period': config[1]}
    tma['long'] = {'period': config[2]}
    tma['tabular'] = {'short': sma_short, 'medium': sma_med, 'long': sma_long}
    tma['metrics'] = {f'{config[0]}-d': m_short, f'{config[1]}-d': m_med, f'{config[2]}-d': m_long}

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    tma['type'] = 'trend'
    tma['length_of_data'] = len(tma['tabular']['short'])
    tma['signals'] = find_crossovers(tma, fund)
    return tma


def triple_exp_mov_average(fund: pd.DataFrame, config: Union[list, None] = None, **kwargs) -> list:
    """Triple Exponential Moving Average

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {str})
        view {str} -- file directory of plots (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Keyword Arguments:
        config {list} -- look back period (default: {[9, 20, 50]})

    Returns:
        list -- plots and signals
    """
    # pylint: disable=too-many-locals
    if not config:
        config = [9, 20, 50]
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    p_bar = kwargs.get('progress_bar')
    out_suppress = kwargs.get('out_suppress', False)

    triple_ema = {}
    t_short = exponential_moving_avg(fund, config[0])
    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    t_med = exponential_moving_avg(fund, config[1])
    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    t_long = exponential_moving_avg(fund, config[2])
    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    triple_ema['tabular'] = {'short': t_short, 'medium': t_med, 'long': t_long}
    triple_ema['short'] = {"period": config[0]}
    triple_ema['medium'] = {"period": config[1]}
    triple_ema['long'] = {"period": config[2]}

    t_short_x, t_short2 = adjust_signals(fund, t_short, offset=config[0])
    t_med_x, t_med2 = adjust_signals(fund, t_med, offset=config[1])
    t_long_x, t_long2 = adjust_signals(fund, t_long, offset=config[2])

    plot_short = {"plot": t_short2, "color": "blue",
                  "legend": f"{config[0]}-day MA", "x": t_short_x}
    plot_med = {"plot": t_med2, "color": "orange",
                "legend": f"{config[1]}-day MA", "x": t_med_x}
    plot_long = {"plot": t_long2,
                 "color": "black", "legend": f"{config[2]}-day MA", "x": t_long_x}

    m_short = []
    m_med = []
    m_long = []

    for i, close in enumerate(fund['Close']):
        m_short.append(np.round((close - t_short[i]) / t_short[i] * 100.0, 3))
        m_med.append(np.round((close - t_med[i]) / t_med[i] * 100.0, 3))
        m_long.append(np.round((close - t_long[i]) / t_long[i] * 100.0, 3))

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    triple_ema['metrics'] = {
        f'{config[0]}-d': m_short,
        f'{config[1]}-d': m_med,
        f'{config[2]}-d': m_long
    }

    if not out_suppress:
        name3 = INDEXES.get(name, name)
        name2 = name3 + f' - Exp Moving Averages [{config[0]}, {config[1]}, {config[2]}]'

        generate_plot(
            PlotType.CANDLESTICKS, fund, **{
                "title": name2, "plot_output": plot_output, "save_fig": True,
                "additional_plots": [plot_short, plot_med, plot_long],
                "filename": os.path.join(name, view, f"exp_moving_averages_{name}.png")
            }
        )

    if p_bar is not None:
        p_bar.uptick(increment=0.2)

    triple_ema['type'] = 'trend'
    triple_ema['length_of_data'] = len(triple_ema['tabular']['short'])
    triple_ema['signals'] = find_crossovers(triple_ema, fund)
    return triple_ema


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
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
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
        short = tma['tabular']['short']
        med = tma['tabular']['medium']
        long = tma['tabular']['long']

    elif function == 'ema':
        if config == []:
            tma = triple_exp_mov_average(
                fund, plot_output=plot_output, name=name,
                out_suppress=out_suppress, view=view)
        else:
            tma = triple_exp_mov_average(
                fund, config=config, plot_output=plot_output,
                name=name, out_suppress=out_suppress, view=view)
        short = tma['tabular']['short']
        med = tma['tabular']['medium']
        long = tma['tabular']['long']

    else:
        return {}

    if progress_bar is not None:
        progress_bar.uptick(increment=0.4)

    mast = {}
    mast['tabular'] = {}
    mast['tabular']['short'] = short
    mast['tabular']['medium'] = med
    mast['tabular']['long'] = long

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
        generate_plot(
            PlotType.SPECIALITY, [fund['Close'], short, med, long, swings],
            **{"alt_ax_index": [4], "legend": legend, "title": name2, "plot_output": plot_output}
        )
    else:
        filename = os.path.join(name, view, f"swing_trades_{function}_{name}.png")
        generate_plot(
            PlotType.SPECIALITY, [fund['Close'], short, med, long, swings], **{
                "alt_ax_index": [4], "legend": ['Swing Signal'], "title": name2, "save_fig": True,
                "plot_output": plot_output, "filename": filename
            }
        )

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    mast['type'] = 'oscillator'
    return mast


def generate_swing_signal(position: pd.DataFrame,
                          swings: dict,
                          max_period: int = 18,
                          config: Union[list, None] = None) -> dict:
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
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    short = swings['tabular']['short']
    med = swings['tabular']['medium']
    long = swings['tabular']['long']

    close = position['Close']
    states = ['n'] * len(close)
    for i in range(max_period, len(states)):
        if (short[i] > med[i]) and (med[i] > long[i]):
            states[i] = 'u3'
        elif (short[i] > med[i]) and (short[i] > long[i]):
            states[i] = 'u2'
        elif (short[i] > med[i]) or (short[i] > long[i]):
            states[i] = 'u1'
        elif (short[i] < med[i]) and (med[i] < long[i]):
            states[i] = 'e3'
        elif (short[i] < med[i]) and (short[i] < long[i]):
            states[i] = 'e2'
        elif (short[i] < med[i]) or (short[i] < long[i]):
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

        if states[i] == 'u2':
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

        elif close[i] > long[i]:
            signal[i] = 0.1

        elif states[i] == 'e2':
            if states[i-1] == 'u3' or states[i-1] == 'u2' or states[i-1] == 'u1':
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

        elif close[i] < long[i]:
            signal[i] = -0.1

        if data is not None:
            features.append(data)

    swings['tabular']['swing'] = signal
    swings['signals'] = features
    swings['length_of_data'] = len(swings['tabular']['swing'])
    return swings


def swing_trade_metrics(position: pd.DataFrame, swings: dict) -> dict:
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
