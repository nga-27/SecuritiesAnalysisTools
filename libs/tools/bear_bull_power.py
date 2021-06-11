import os
import pandas as pd
from scipy.stats import linregress

from libs.utils import bar_chart, dual_plotting, dates_extractor_list, INDEXES
from libs.tools import exponential_moving_avg
from libs.features import normalize_signals


def bear_bull_power(position: pd.DataFrame, **kwargs) -> dict:
    """Bear Bull Power

    Arguments:
        position {pd.DataFrame} -- dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        progress_bar {ProgressBar} -- (default: {None})
        name {str} -- (default: {''})
        view {str} -- directory of plots (default: {''})

    Returns:
        dict -- [description]
    """
    p_bar = kwargs.get('progress_bar')
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')

    bbp = dict()

    bbp['tabular'] = generate_bear_bull_signal(
        position, plot_output=plot_output, name=name, p_bar=p_bar, view=view)
    bbp = bear_bull_feature_detection(
        bbp, position, plot_output=plot_output, name=name, p_bar=p_bar, view=view)

    bbp['type'] = 'oscillator'

    return bbp


def generate_bear_bull_signal(position: pd.DataFrame, **kwargs) -> dict:
    """Generate Bear Bull Signal

    Arguments:
        position {pd.DataFrame} -- dataset

    Optional Args:
        interval {int} -- size of exponential moving average window (default: {13})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- [description]
    """
    interval = kwargs.get('interval', 13)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('p_bar')

    bb_signal = {'bulls': [], 'bears': []}
    ema = exponential_moving_avg(position, interval)

    for i, high in enumerate(position['High']):
        bb_signal['bulls'].append(high - ema[i])

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    for i, low in enumerate(position['Low']):
        bb_signal['bears'].append(low - ema[i])

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    x = dates_extractor_list(position)
    if plot_output:
        name3 = INDEXES.get(name, name)
        name2 = name3 + ' - Bull Power'
        bar_chart(bb_signal['bulls'], position=position, title=name2, x=x)
        name2 = name3 + ' - Bear Power'
        bar_chart(bb_signal['bears'], position=position, title=name2, x=x)

    return bb_signal


def bear_bull_feature_detection(bear_bull: dict, position: pd.DataFrame, **kwargs) -> dict:
    """Bear Bull Feature Detection

    Arguments:
        bear_bull {dict} -- bull bear data object
        position {pd.DataFrame} -- dataset

    Optional Args:
        interval {int} -- size of exponential moving average window (default: {13})
        bb_interval {list} -- list of sizes of bear and bull windows (default: {[4, 5, 6, 7, 8]})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default {None})
        view {str} -- (default: {''})

    Returns:
        dict -- [description]
    """
    interval = kwargs.get('interval', 13)
    bb_interval = kwargs.get('bb_interval', [4, 5, 6, 7, 8])
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('p_bar')
    view = kwargs.get('view')

    # Determine the slope of the ema at given points
    ema = exponential_moving_avg(position, interval)

    ema_slopes = [0.0] * (interval-1)
    for i in range(interval-1, len(ema)):
        x = list(range(i-(interval-1), i))
        y = ema[i-(interval-1): i]
        reg = linregress(x, y=y)
        ema_slopes.append(reg[0])

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    incr = 0.6 / float(len(bb_interval))

    state = [0.0] * len(ema)
    features = []

    for bb in bb_interval:
        # Determine the slope of the bear power signal at given points
        bear_slopes = [0.0] * (bb-1)
        for i in range(bb-1, len(ema)):
            x = list(range(i-(bb-1), i))
            y = bear_bull['tabular']['bears'][i-(bb-1): i]
            reg = linregress(x, y=y)
            bear_slopes.append(reg[0])

        # Determine the slope of the bull power signal at given points
        bull_slopes = [0.0] * (bb-1)
        for i in range(bb-1, len(ema)):
            x = list(range(i-(bb-1), i))
            y = bear_bull['tabular']['bulls'][i-(bb-1): i]
            reg = linregress(x, y=y)
            bull_slopes.append(reg[0])

        for i in range(1, len(ema)):
            data = None
            date = position.index[i].strftime("%Y-%m-%d")

            if ema_slopes[i] > 0.0:
                if bear_bull['tabular']['bears'][i] < 0.0:
                    if bear_slopes[i] > 0.0:
                        # Determine the basic (first 2 conditions) bullish state (+1)
                        state[i] += 1.0
                        if bear_bull['tabular']['bulls'][i] > bear_bull['tabular']['bulls'][i-1]:
                            state[i] += 0.5
                            if position['Close'][i] < position['Close'][i-1]:
                                # Need to find bullish divergence!
                                state[i] += 1.0
                                data = {
                                    "type": 'bullish',
                                    "value": f'bullish divergence: {bb}d interval',
                                    "index": i,
                                    "date": date
                                }

            if ema_slopes[i] < 0.0:
                if bear_bull['tabular']['bulls'][i] > 0.0:
                    if bull_slopes[i] < 0.0:
                        # Determine the basic (first 2 conditions) bearish state (+1)
                        state[i] += -1.0
                        if bear_bull['tabular']['bears'][i] < bear_bull['tabular']['bears'][i-1]:
                            state[i] += -0.5
                            if position['Close'][i] > position['Close'][i-1]:
                                # Need to find bearish divergence!
                                state[i] += -1.0
                                data = {
                                    "type": 'bearish',
                                    "value": f'bearish divergence: {bb}d interval',
                                    "index": i,
                                    "date": date
                                }

            if data is not None:
                features.append(data)

        if p_bar is not None:
            p_bar.uptick(increment=incr)

    bear_bull['signals'] = filter_features(features, plot_output=plot_output)
    bear_bull['length_of_data'] = len(bear_bull['tabular']['bears'])

    weights = [1.0, 0.75, 0.45, 0.1]

    state2 = [0.0] * len(state)
    for ind, s in enumerate(state):
        if s != 0.0:
            state2[ind] += s

            # Smooth the curves
            if ind - 1 >= 0:
                state2[ind-1] += s * weights[1]
            if ind + 1 < len(state):
                state2[ind+1] += s * weights[1]
            if ind - 2 >= 0:
                state2[ind-2] += s * weights[2]
            if ind + 2 < len(state):
                state2[ind+2] += s * weights[2]
            if ind - 3 >= 0:
                state2[ind-3] += s * weights[3]
            if ind + 3 < len(state):
                state2[ind+3] += s * weights[3]

    state3 = exponential_moving_avg(state2, 7, data_type='list')
    norm = normalize_signals([state3])
    state4 = norm[0]

    title = 'Bear Bull Power Metrics'
    if plot_output:
        dual_plotting(position['Close'], state4, 'Price',
                      'Bear Bull Power', title=title)
    else:
        filename = os.path.join(name, view, f"bear_bull_power_{name}.png")
        dual_plotting(position['Close'], state4, 'Price', 'Metrics', title=title,
                      saveFig=True, filename=filename)

    bear_bull['metrics'] = state4

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    return bear_bull


def filter_features(feature_list: list, plot_output=False) -> list:
    """Filter Features

    Many features are duplicates based off intervals above; only accept first one.

    Arguments:
        feature_list {list} -- list of features from feature detection above

    Keyword Arguments:
        plot_output {bool} -- (default: {False})

    Returns:
        list -- filtered feature list
    """
    feature_list.sort(key=lambda x: x['index'])
    new_list = []
    latest_index = 0
    for feat in feature_list:
        if feat['index'] != latest_index:
            new_list.append(feat)
            latest_index = feat['index']
            if plot_output:
                print(f"BearBullPower: {feat}")

    return new_list
