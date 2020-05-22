import os
import pprint
from copy import deepcopy
import pandas as pd
import numpy as np

from libs.utils import ProgressBar, INDEXES
from libs.utils import candlestick_plot
from .moving_average import simple_moving_avg, exponential_moving_avg
from .full_stochastic import generate_full_stoch_signal


def candlesticks(fund: pd.DataFrame, **kwargs) -> dict:
    """Candlesticks

    Generate Candlestick plots and data formation

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- candlestick data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('progress_bar')

    candle = dict()

    candle['thresholds'] = thresholding_determination(
        fund, plot_output=plot_output)
    if pbar is not None:
        pbar.uptick(increment=0.1)

    candle['classification'] = day_classification(fund, candle['thresholds'])
    if pbar is not None:
        pbar.uptick(increment=0.1)

    candle = pattern_detection(
        fund, candle, plot_output=plot_output, pbar=pbar)

    candle['signals'] = get_pattern_signals(candle, fund)
    candle['length_of_data'] = len(fund.index)

    fifty_day = simple_moving_avg(fund, 50)
    two_hundred_day = simple_moving_avg(fund, 200)
    plot_50 = {"plot": fifty_day, "color": "blue", "legend": "50-day MA"}
    plot_200 = {"plot": two_hundred_day,
                "color": "black", "legend": "200-day MA"}

    name2 = INDEXES.get(name, name)

    if plot_output:
        candlestick_plot(fund, title=name2, additional_plts=[
                         plot_50, plot_200])
    else:
        filename = os.path.join(name, view, f"candlestick_{name}.png")
        candlestick_plot(fund, title=name2, filename=filename,
                         saveFig=True, additional_plts=[plot_50, plot_200])

    if pbar is not None:
        pbar.uptick(increment=0.1)
    return candle


def pattern_detection(fund: pd.DataFrame, candle: dict, **kwargs) -> dict:
    """Pattern Detection

    Searches available candlestick patterns on each area of the dataset

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        candle {dict} -- candlestick data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        pbar {ProgressBar} -- (default: {None})

    Returns:
        dict -- candlestick data object
    """
    plot_output = kwargs.get('plot_output', True)
    pbar = kwargs.get('pbar')

    if pbar is not None:
        divisor = 0.7 / float(len(candle['classification']))

    patterns = []
    for i in range(len(candle['classification'])):
        value = {'value': 0, 'patterns': []}
        for patt in PATTERNS:
            val = pattern_library(patt, candle['classification'], i)
            if val[0] != 0:
                value['value'] += val[0]
                modified_pattern = f"{patt}: {val[1]}"
                value['patterns'].append(modified_pattern)

        for patt in PATTERNS:
            val = pattern_library(
                patt, candle['classification'], i, body='vol_body')
            if val[0] != 0:
                value['value'] += val[0]
                modified_pattern = f"{patt}: {val[1]}"
                value['patterns'].append(modified_pattern)

        if pbar is not None:
            pbar.uptick(increment=divisor)

        patterns.append(value)

    patterns2 = filtered_reversal_patterns(fund, candle)
    tabular = [0.0] * len(patterns)

    for i, patt in enumerate(patterns2):
        if patt['value'] != 0:
            patterns[i]['value'] += patt['value']
            patterns[i]['patterns'].extend(patt['patterns'])

    for i, patt in enumerate(patterns):
        tabular[i] += float(patt['value'])

    if plot_output:
        signal = simple_moving_avg(fund, 10)

        for i, patt in enumerate(patterns):
            if patt['value'] != 0:
                signal[i] += (patt['value'] * 10.0)
                print(f"index {i}: {patt['value']} => {patt['patterns']}")

        plot_obj = {"plot": signal, "color": 'black',
                    "legend": 'candlestick signal'}
        candlestick_plot(fund, additional_plts=[
            plot_obj], title='Candlestick Signals')

    candle['patterns'] = patterns
    candle['tabular'] = tabular

    return candle


def thresholding_determination(fund: pd.DataFrame, **kwargs) -> dict:
    """Thresholding Determination

    Dynamically determine what a "long day", "short day", and a "doji" is.

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        long_percentile {int} -- lower limit to "long day" body size (default: {85})
        short_percentile {int} -- upper limit to "short day" body size (default: {25})
        doji_percentile {int} -- upper limit to "doji" body size (default: {1})
        doji_ratio {int} -- shadow (high-low) / body (close-open) ratio (default: {8})
        plot_output {bool} -- (default: {True})

    Returns:
        dict -- thresholding values
    """
    LONG = kwargs.get('long_percentile', 75)
    SHORT = kwargs.get('short_percentile', 25)
    DOJI = kwargs.get('doji_percentile', 1)
    DOJI_RATIO = kwargs.get('doji_ratio', 8)
    plot_output = kwargs.get('plot_output', True)

    open_close = []
    high_low = []
    for i, op in enumerate(fund['Open']):
        open_close.append(np.abs(op - fund['Close'][i]))
        high_low.append(np.abs(fund['High'][i] - fund['Low'][i]))

    volatility = exponential_moving_avg(high_low, 25, data_type='list')
    long_price = []
    short_price = []
    long_thresh = float(LONG) / 100.0
    short_thresh = float(SHORT) * 2.0 / 100.0
    for i, low in enumerate(fund['Low']):
        price_l = low + (volatility[i] * long_thresh)
        price_s = low + (volatility[i] * short_thresh)
        long_price.append(price_l)
        short_price.append(price_s)

    thresholds = dict()
    thresholds['short'] = np.percentile(open_close, SHORT)
    thresholds['long'] = np.percentile(open_close, LONG)
    thresholds['doji'] = np.percentile(open_close, DOJI)
    thresholds['doji_ratio'] = DOJI_RATIO
    thresholds['volatility'] = {"long": long_price, "short": short_price}

    if plot_output:
        print(f"\r\nThresholding for candlesticks:")
        print(f"\r\nShort: {thresholds['short']}")
        print(f"Long: {thresholds['long']}")
        print(f"Doji: {thresholds['doji']}")
        print(f"Doji Ratio: {thresholds['doji_ratio']}")
        candlestick_plot(fund, title="Doji & Long/Short Days",
                         threshold_candles=thresholds)

    return thresholds


def day_classification(fund: pd.DataFrame, thresholds: dict) -> list:
    """Day Classification

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        thresholds {dict} -- candlestick body sizes

    Returns:
        list -- each trading period classified by candlesticks
    """
    days = []
    sma = simple_moving_avg(fund, 10)

    LONG = thresholds['long']
    SHORT = thresholds['short']
    DOJI = thresholds['doji']
    RATIO = thresholds['doji_ratio']

    vol_long = thresholds['volatility']['long']
    vol_short = thresholds['volatility']['short']

    # Classification elements:
    for i, close in enumerate(fund['Close']):
        stats = dict()

        # Raw, basic values to start
        stats['basic'] = dict()
        stats['basic']['Close'] = close
        stats['basic']['Open'] = fund['Open'][i]
        stats['basic']['High'] = fund['High'][i]
        stats['basic']['Low'] = fund['Low'][i]

        # Where close appears vs. Trend (sma-10)
        if close > sma[i]:
            stats['trend'] = 'above'
        elif close < sma[i]:
            stats['trend'] = 'below'
        else:
            stats['trend'] = 'at'

        # Candlestick-esc properties
        stats['candlestick'] = dict()

        diff = np.abs(close - fund['Open'][i])
        shadow_length = fund['High'][i] - fund['Low'][i]

        if diff >= LONG:
            stats['candlestick']['body'] = 'long'
        elif diff <= SHORT:
            stats['candlestick']['body'] = 'short'
        else:
            stats['candlestick']['body'] = 'normal'

        if fund['High'][i] > vol_long[i]:
            stats['candlestick']['vol_body'] = 'long'
        elif fund['High'][i] < vol_short[i]:
            stats['candlestick']['vol_body'] = 'short'
        else:
            stats['candlestick']['vol_body'] = 'normal'

        if close > fund['Open'][i]:
            stats['candlestick']['color'] = 'white'
        else:
            stats['candlestick']['color'] = 'black'

        stats['candlestick']['doji'] = False
        stats['candlestick']['shadow_ratio'] = 0.0
        if diff > 0.0:
            stats['candlestick']['shadow_ratio'] = shadow_length / diff
        if diff <= DOJI:
            if stats['candlestick']['shadow_ratio'] >= RATIO:
                stats['candlestick']['doji'] = True

        days.append(stats)
    return days


def get_pattern_signals(candle: dict, position: pd.DataFrame) -> list:
    """Get Pattern Signals

    Specifically for lastest signals present

    Arguments:
        candle {dict} -- candle data object
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of feature objects
    """
    features = []
    for i, patt in enumerate(candle['patterns']):
        date = position.index[i].strftime("%Y-%m-%d")

        if patt['value'] < 0:
            for style in patt['patterns']:
                data = {
                    "type": 'bearish',
                    "value": style,
                    "index": i,
                    "date": date
                }
                features.append(data)

        elif patt['value'] > 0:
            for style in patt['patterns']:
                data = {
                    "type": 'bullish',
                    "value": style,
                    "index": i,
                    "date": date
                }
                features.append(data)

    return features


def filtered_reversal_patterns(fund: pd.DataFrame,
                               candle: dict,
                               filter_function='stochastic') -> list:
    """Filtered Reversal Patterns

    citing Greg Morris: Pattern must be in oscillator extreme to be valid

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        candle {dict} -- candlestick data object

    Keyword Arguments:
        filter_function {str} -- oscillator of choice (default: {'stochastic'})

    Returns:
        list -- list of detected pattern objects
    """
    filter_signal = []
    ZONES = [0.0, 0.0]
    if filter_function == 'stochastic':
        stoch_signals = generate_full_stoch_signal(fund, plot_output=False)
        filter_signal = stoch_signals['smooth_k']
        ZONES = [80.0, 20.0]
    else:
        return []

    patterns = []
    for i in range(len(candle['classification'])):
        value = {'value': 0, 'patterns': []}

        val = pattern_library("dark_cloud_piercing_line",
                              candle['classification'], i)
        if val[0] != 0:
            value['value'] += val[0]
            modified_pattern = f"dark_cloud_piercing_line: {val[1]}"
            value['patterns'].append(modified_pattern)

        val = pattern_library("evening_morning_star",
                              candle['classification'], i)
        if val[0] != 0:
            value['value'] += val[0]
            modified_pattern = f"evening_morning_star: {val[1]}"
            value['patterns'].append(modified_pattern)

        val = pattern_library("dark_cloud_piercing_line",
                              candle['classification'], i, body='vol_body')
        if val[0] != 0:
            value['value'] += val[0]
            modified_pattern = f"dark_cloud_piercing_line: {val[1]}"
            value['patterns'].append(modified_pattern)

        val = pattern_library("evening_morning_star",
                              candle['classification'], i, body='vol_body')
        if val[0] != 0:
            value['value'] += val[0]
            modified_pattern = f"evening_morning_star: {val[1]}"
            value['patterns'].append(modified_pattern)

        patterns.append(value)

    for i in range(1, len(patterns)):
        if patterns[i]['value'] != 0:
            if (filter_signal[i] >= ZONES[0]) and (filter_signal[i] <= ZONES[1]):
                patterns[i]['value'] *= 2
            elif (filter_signal[i-1] >= ZONES[0]) and (filter_signal[i-1] <= ZONES[1]):
                patterns[i]['value'] *= 2
            else:
                patterns[i] = {'value': 0, 'patterns': []}

    return patterns


###################################
#   PATTERN DETECTION LIBRARY
###################################

def pattern_library(pattern: str, days: list, index: int, body: str = 'body') -> list:
    """Pattern Library

    Command function for properly configuring and running various pattern detections.

    Arguments:
        pattern {str} -- key from PATTERNS object
        days {list} -- candle objects generated from day_classification
        index {int} -- index of DataFrame or list

    Keyword Arguments:
        body {str} -- body generation style (quartile vs. volatility); (default: {'body'})

    Returns:
        list -- tuple (value of patterns, named pattern)
    """
    days_needed = PATTERNS.get(pattern, {}).get('days', 1)
    function = PATTERNS.get(pattern, {}).get('function')
    weight = PATTERNS.get(pattern, {}).get('weight', 1)

    if function is None:
        return 0, ''
    if index < days_needed - 1:
        return 0, ''

    if days_needed == 1:
        sub_days = days[index].copy()
    else:
        start = (index + 1) - days_needed
        sub_days = days[start:index+1].copy()

    if isinstance(sub_days, (dict)):
        sub_days = [sub_days]

    detection = function(sub_days, body=body)
    if detection is not None:
        if detection['type'] == 'bearish':
            return -1 * weight, detection['style']
        if detection['type'] == 'bullish':
            return 1 * weight, detection['style']

    return 0, ''


###################################

def doji_pattern(day: list, body='body') -> dict:
    THRESH = 0.05
    day = day[0]
    if day.get('candlestick', {}).get('doji'):
        close = day.get('basic', {}).get('Close')
        high = day.get('basic', {}).get('High')
        low = day.get('basic', {}).get('Low')

        clo_low = close - low
        hi_low = high - low
        if clo_low >= ((1.0 - THRESH) * hi_low):
            return {'type': 'bullish', 'style': 'dragonfly'}
        if clo_low <= (THRESH * hi_low):
            return {'type': 'bearish', 'style': 'gravestone'}
    return None


def dark_cloud_or_piercing_line(day: list, body='body') -> dict:
    # Dark Cloud
    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get(body) == 'long':
            if candle_0.get('color') == 'white':
                basic_0 = day[0].get('basic')
                high_0 = basic_0.get('High')
                basic_1 = day[1].get('basic')
                open_1 = basic_1.get('Open')
                if open_1 > high_0:
                    close_1 = basic_1.get('Close')
                    close_0 = basic_0.get('Close')
                    open_0 = basic_0.get('Open')
                    mid_pt = ((close_0 - open_0) / 2.0) + open_0
                    if close_1 <= mid_pt:
                        return {'type': 'bearish', 'style': 'darkcloud'}

    # Piercing Line
    elif day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get(body) == 'long':
            if candle_0.get('color') == 'black':
                basic_0 = day[0].get('basic')
                low_0 = basic_0.get('Low')
                basic_1 = day[1].get('basic')
                open_1 = basic_1.get('Open')
                if open_1 < low_0:
                    close_1 = basic_1.get('Close')
                    close_0 = basic_0.get('Close')
                    open_0 = basic_0.get('Open')
                    mid_pt = ((close_0 - open_0) / 2.0) + open_0
                    if close_1 >= mid_pt:
                        return {'type': 'bullish', 'style': 'piercing line'}

    return None


def evening_morning_star(day: list, body='body') -> dict:
    # Evening star
    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            basic_0 = day[0].get('basic')
            basic_1 = day[1].get('basic')
            close_0 = basic_0.get('Close')
            open_1 = basic_1.get('Open')
            if open_1 > close_0:
                candle_1 = day[1].get('candlestick')
                if candle_1[body] == 'short':
                    close_1 = basic_1.get('Close')
                    if close_1 > close_0:
                        basic_2 = day[2].get('basic')
                        open_2 = basic_2.get('Open')
                        if open_2 < min(close_1, open_1):
                            open_0 = basic_0.get('Open')
                            mid_pt = ((close_0 - open_0) / 2.0) + open_0
                            close_2 = basic_2.get('Close')
                            if close_2 <= mid_pt:
                                if candle_1['doji']:
                                    if basic_1['Low'] > max(basic_0['High'], basic_1['High']):
                                        return {"type": 'bearish', "style": 'abandoned baby -'}
                                    return {"type": 'bearish', "style": 'evening star DOJI'}
                                return {'type': 'bearish', 'style': 'evening star'}

    # Morning star
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            basic_0 = day[0].get('basic')
            basic_1 = day[1].get('basic')
            close_0 = basic_0.get('Close')
            open_1 = basic_1.get('Open')
            if open_1 < close_0:
                candle_1 = day[1].get('candlestick')
                if candle_1[body] == 'short':
                    close_1 = basic_1.get('Close')
                    if close_1 < close_0:
                        basic_2 = day[2].get('basic')
                        open_2 = basic_2.get('Open')
                        if open_2 > max(close_1, open_1):
                            open_0 = basic_0.get('Open')
                            mid_pt = ((close_0 - open_0) / 2.0) + open_0
                            close_2 = basic_2.get('Close')
                            if close_2 >= mid_pt:
                                if candle_1['doji']:
                                    if basic_1['High'] < min(basic_0['Low'], basic_1['Low']):
                                        return {"type": 'bullish', "style": 'abandoned baby +'}
                                    return {"type": 'bullish', "style": 'morning star: DOJI'}
                                return {'type': 'bullish', 'style': 'morning star'}
    return None


def rising_falling_three_methods(day: list, body='body') -> dict:
    # Rising three methods (continuation of bull trend)
    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            basic_0 = day[0].get('basic')
            high_0 = basic_0.get('High')
            low_0 = basic_0.get('Low')
            close_0 = basic_0.get('Close')
            basic_1 = day[1].get('basic')
            if high_0 >= max(basic_1.get('Open'), basic_1.get('Close')):
                if low_0 <= min(basic_1.get('Open'), basic_1.get('Close')):
                    if day[1]['candlestick'][body] == 'short':
                        basic_2 = day[1].get('basic')
                        if high_0 >= max(basic_2.get('Open'), basic_2.get('Close')):
                            if low_0 <= min(basic_2.get('Open'), basic_2.get('Close')):
                                basic_3 = day[1].get('basic')
                                if high_0 >= max(basic_3.get('Open'), basic_3.get('Close')):
                                    if low_0 <= min(basic_3.get('Open'), basic_3.get('Close')):
                                        candle_4 = day[4].get(
                                            'candlestick')
                                        if candle_4[body] == 'long' and \
                                                candle_4['color'] == 'white':
                                            if day[4].get('basic', {}).get('Close') > close_0:
                                                return {"type": 'bullish',
                                                        "style": 'rising three methods'}

    # Falling three methods (continuation of bear trend)
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            basic_0 = day[0].get('basic')
            high_0 = basic_0.get('High')
            low_0 = basic_0.get('Low')
            close_0 = basic_0.get('Close')
            basic_1 = day[1].get('basic')
            if low_0 <= min(basic_1.get('Open'), basic_1.get('Close')):
                if high_0 >= max(basic_1.get('Open'), basic_1.get('Close')):
                    if day[1]['candlestick'][body] == 'short':
                        basic_2 = day[1].get('basic')
                        if low_0 <= min(basic_2.get('Open'), basic_2.get('Close')):
                            if high_0 >= max(basic_2.get('Open'), basic_2.get('Close')):
                                basic_3 = day[1].get('basic')
                                if low_0 <= min(basic_3.get('Open'), basic_3.get('Close')):
                                    if high_0 >= max(basic_3.get('Open'), basic_3.get('Close')):
                                        candle_4 = day[4].get(
                                            'candlestick')
                                        if candle_4[body] == 'long' and \
                                                candle_4['color'] == 'black':
                                            if day[4].get('basic', {}).get('Close') < close_0:
                                                return {"type": 'bearish',
                                                        "style": 'falling three methods'}
    return None


def hammer_positive(day: list, body='body') -> dict:
    RATIO = 2.0
    THRESH = 0.99
    if day[0].get('trend') == 'below':
        candle = day[0].get('candlestick')
        if candle[body] == 'short' and candle['shadow_ratio'] >= RATIO:
            basic = day[0].get('basic')
            high = basic.get('High')
            close = basic.get('Close')
            _open = basic.get('Open')
            low = basic.get('Low')
            hl_thr = (high - low) * THRESH
            cl_low = close - low
            op_low = _open - low
            if (cl_low >= hl_thr) or (op_low >= hl_thr):
                return {"type": 'bullish', "style": '+'}
    return None


def hanging_man(day: list, body='body') -> dict:
    RATIO = 2.0
    THRESH = 0.99
    if day[0].get('trend') == 'above':
        candle = day[0].get('candlestick')
        if candle[body] == 'short' and candle['shadow_ratio'] >= RATIO:
            basic = day[0].get('basic')
            high = basic.get('High')
            close = basic.get('Close')
            _open = basic.get('Open')
            low = basic.get('Low')
            hl_thr = (high - low) * THRESH
            cl_low = close - low
            op_low = _open - low
            if (cl_low >= hl_thr) or (op_low >= hl_thr):
                return {"type": 'bearish', "style": '-'}
    return None


def inverted_hammer(day: list, body='body') -> dict:
    RATIO = 2.0
    THRESH = 0.01
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = day[1].get('candlestick')
            if candle_1[body] == 'short' and candle_1['shadow_ratio'] >= RATIO:
                basic = day[1].get('basic')
                high = basic.get('High')
                close = basic.get('Close')
                _open = basic.get('Open')
                low = basic.get('Low')
                hl_thr = (high - low) * THRESH
                cl_low = close - low
                op_low = _open - low
                if (cl_low <= hl_thr) or (op_low <= hl_thr):
                    return {"type": 'bullish', "style": '+'}
    return None


def shooting_star(day: list, body='body') -> dict:
    RATIO = 2.0
    THRESH = 0.01
    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            basic_0 = day[0].get('basic')
            if basic_0.get('Close') < basic_0.get('High'):
                candle_1 = day[1].get('candlestick')
                if candle_1[body] == 'short' and candle_1['shadow_ratio'] >= RATIO:
                    basic_1 = day[1].get('basic')
                    high = basic_1.get('High')
                    low = basic_1.get('Low')
                    close = basic_1.get('Close')
                    _open = basic_1.get('Open')
                    if (_open > basic_0.get('Close')) and (close > basic_0.get('Close')):
                        hl_thr = (high - low) * THRESH
                        cl_low = close - low
                        op_low = _open - low
                        if (cl_low <= hl_thr) or (op_low <= hl_thr):
                            return {"type": 'bearish', "style": '-'}
    return None


def belt_hold(day: list, body='body') -> dict:
    THRESH = 0.005
    if day[0].get('trend') == 'below':
        candle = day[0].get('candlestick')
        if candle.get('color') == 'white':
            basic = day[0].get('basic')
            high = basic.get('High')
            _open = basic.get('Open')
            low = basic.get('Low')
            hl_thr = (high - low) * THRESH
            op_low = _open - low
            if (op_low <= hl_thr) and (high > basic.get('Close')):
                return {"type": 'bullish', "style": '+'}

    if day[0].get('trend') == 'above':
        candle = day[0].get('candlestick')
        if candle.get('color') == 'black':
            basic = day[0].get('basic')
            high = basic.get('High')
            _open = basic.get('Open')
            low = basic.get('Low')
            hl_thr = (high - low) * (1.0 - THRESH)
            op_low = _open - low
            if (op_low >= hl_thr) and (low < basic.get('Close')):
                return {"type": 'bearish', "style": '-'}
    return None


def engulfing(day: list, body='body') -> dict:
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'black':
            candle_1 = day[1].get('candlestick')
            if candle_1[body] == 'long' and candle_1['color'] == 'white':
                basic_0 = day[0].get('basic')
                basic_1 = day[1].get('basic')
                if basic_0.get('High') <= basic_1.get('Close'):
                    if basic_0.get('Low') >= basic_1.get('Open'):
                        return {"type": 'bullish', "style": '+'}

    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'white':
            candle_1 = day[1].get('candlestick')
            if candle_1[body] == 'long' and candle_1['color'] == 'black':
                basic_0 = day[0].get('basic')
                basic_1 = day[1].get('basic')
                if basic_0.get('High') <= basic_1.get('Open'):
                    if basic_0.get('Low') >= basic_1.get('Close'):
                        return {"type": 'bearish', "style": '-'}
    return None


def harami(day: list, body='body') -> dict:
    THRESH = 0.01
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0['color'] == 'black' and candle_0[body] == 'long':
            candle_1 = day[1].get('candlestick')
            if candle_1.get('color') == 'white':
                basic_0 = day[0].get('basic')
                basic_1 = day[1].get('basic')
                if basic_1.get('High') <= basic_0.get('Open'):
                    if basic_1.get('Low') >= basic_1.get('Close'):
                        hi_low = basic_1.get('High') - basic_1.get('Low')
                        op_clo = np.abs(basic_1.get(
                            'Close') - basic_1.get('Open'))
                        if op_clo <= (hi_low * THRESH):
                            return {"type": 'bullish', "style": 'cross-+'}
                        return {"type": 'bullish', "style": "+"}

    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0['color'] == 'white' and candle_0[body] == 'long':
            candle_1 = day[1].get('candlestick')
            if candle_1.get('color') == 'black':
                basic_0 = day[0].get('basic')
                basic_1 = day[1].get('basic')
                if basic_1.get('High') <= basic_0.get('Close'):
                    if basic_1.get('Low') >= basic_1.get('Open'):
                        hi_low = basic_1.get('High') - basic_1.get('Low')
                        op_clo = np.abs(basic_1.get(
                            'Open') - basic_1.get('Close'))
                        if op_clo <= (hi_low * THRESH):
                            return {"type": 'bearish', "style": 'cross--'}
                        return {"type": 'bearish', "style": "-"}
    return None


def doji_star(day: list, body='body') -> dict:
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0['color'] == 'black' and candle_0[body] != 'short':
            basic_1 = day[1].get('basic')
            basic_0 = day[0].get('basic')
            if basic_1.get('High') <= basic_0.get('Close'):
                candle_1 = day[1].get('candlestick')
                if candle_1.get('doji'):
                    return {"type": 'bullish', "style": "+"}

    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0['color'] == 'white' and candle_0[body] != 'short':
            basic_1 = day[1].get('basic')
            basic_0 = day[0].get('basic')
            if basic_1.get('Low') >= basic_0.get('Close'):
                candle_1 = day[1].get('candlestick')
                if candle_1.get('doji'):
                    return {"type": 'bearish', "style": "-"}
    return None


def meeting_line(day: list, body='body') -> dict:
    THRESH = 0.01
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0[body] != 'short' and candle_0['color'] == 'black':
            candle_1 = day[1].get('candlestick')
            if candle_1['color'] == 'white' and candle_1[body] != 'short':
                basic_1 = day[1].get('basic')
                basic_0 = day[0].get('basic')
                hl_thr = (basic_1.get('High') -
                          basic_1.get('Low')) * THRESH
                cl_cl = np.abs(basic_0.get('Close') -
                               basic_1.get('Close'))
                if cl_cl <= hl_thr:
                    return {"type": 'bullish', "style": "+"}

    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0[body] != 'short' and candle_0['color'] == 'white':
            candle_1 = day[1].get('candlestick')
            if candle_1['color'] == 'black' and candle_1[body] != 'short':
                basic_1 = day[1].get('basic')
                basic_0 = day[0].get('basic')
                hl_thr = (basic_1.get('High') -
                          basic_1.get('Low')) * THRESH
                cl_cl = np.abs(basic_0.get('Close') -
                               basic_1.get('Close'))
                if cl_cl <= hl_thr:
                    return {"type": 'bearish', "style": "-"}
    return None


def three_white_soldiers_black_crows(day: list, body='body') -> dict:
    THRESH = 0.3
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0['color'] == 'white' and candle_0[body] != 'short':
            candle_1 = day[1].get('candlestick')
            if candle_1['color'] == 'white' and candle_1[body] != 'short':
                basic_0 = day[0].get('basic')
                basic_1 = day[1].get('basic')
                body_th = ((basic_0.get('Close') - basic_0.get('Open'))
                           * THRESH) + basic_0.get('Open')
                if (basic_1.get('Open') > body_th) and (basic_1['Close'] > basic_0['Close']) \
                        and (basic_1['Open'] < basic_0['Close']):
                    candle_2 = day[2].get('candlestick')
                    if candle_2['color'] == 'white' and candle_2[body] != 'short':
                        basic_2 = day[2].get('basic')
                        body_th = (
                            (basic_1['Close'] - basic_1['Open']) * THRESH) + basic_1['Open']
                        if (basic_2['Open'] > body_th) and (basic_2['Close'] > basic_1['Close']) \
                                and (basic_2['Open'] < basic_1['Close']):
                            return {"type": 'bullish', "style": 'white soldiers'}

    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0['color'] == 'black' and candle_0[body] != 'short':
            candle_1 = day[1].get('candlestick')
            if candle_1['color'] == 'black' and candle_1[body] != 'short':
                basic_0 = day[0].get('basic')
                basic_1 = day[1].get('basic')
                body_th = ((basic_0.get('Close') - basic_0.get('Open'))
                           * (1.0 - THRESH)) + basic_0.get('Open')
                if (basic_1.get('Open') < body_th) and (basic_1['Close'] < basic_0['Close']) \
                        and (basic_1['Open'] > basic_0['Close']):
                    candle_2 = day[2].get('candlestick')
                    if candle_2['color'] == 'black' and candle_2[body] != 'short':
                        basic_2 = day[2].get('basic')
                        body_th = (
                            (basic_1['Close'] - basic_1['Open']) * (1.0 - THRESH)) + basic_1['Open']
                        if (basic_2['Open'] < body_th) and \
                            (basic_2['Close'] < basic_1['Close']) and \
                                (basic_2['Open'] > basic_1['Close']):
                            return {"type": 'bearish', "style": 'black crows'}
    return None


def tri_star(day: list, body='body') -> dict:
    if day[0]['trend'] == 'below':
        if day[0]['candlestick']['doji'] and \
            day[1]['candlestick']['doji'] and \
                day[2]['candlestick']['doji']:
            if day[1]['basic']['Close'] < day[0]['basic']['Close']:
                if day[1]['basic']['Close'] < day[2]['basic']['Close']:
                    return {"type": 'bullish', "style": 'tri star +'}

    if day[0]['trend'] == 'above':
        if day[0]['candlestick']['doji'] and \
            day[1]['candlestick']['doji'] and \
                day[2]['candlestick']['doji']:
            if day[1]['basic']['Close'] > day[0]['basic']['Close']:
                if day[1]['basic']['Close'] > day[2]['basic']['Close']:
                    return {"type": 'bearish', "style": 'tri star -'}
    return None


def breakaway(day: list, body='body') -> dict:
    if day[0]['trend'] == 'below':
        if day[0]['candlestick'][body] == 'long' and day[0]['candlestick']['color'] == 'black':
            if day[0]['basic']['Low'] > day[1]['basic']['High']:
                candle_1 = day[1]['candlestick']
                if candle_1[body] == 'short' and candle_1['color'] == 'black':
                    basic_2 = day[2]['basic']
                    basic_1 = day[1]['basic']
                    if (basic_2['Close'] < basic_1['Open']) and (basic_2['Open'] < basic_1['Open']):
                        if basic_2['Low'] < basic_1['Low']:
                            candle_3 = day[3]['candlestick']
                            if candle_3[body] == 'short' and candle_3['color'] == 'black':
                                if day[3]['basic']['Low'] < basic_2['Low']:
                                    candle_4 = day[4]['candlestick']
                                    if candle_4[body] == 'long' and candle_4['color'] == 'white':
                                        basic_4 = day[4]['basic']
                                        if (basic_4['Close'] > basic_1['Open']) and \
                                                (basic_4['Close'] <= day[0]['basic']['Close']):
                                            return {"type": 'bullish', "style": 'breakaway +'}

    if day[0]['trend'] == 'above':
        if day[0]['candlestick'][body] == 'long' and day[0]['candlestick']['color'] == 'white':
            if day[0]['basic']['High'] < day[1]['basic']['Low']:
                candle_1 = day[1]['candlestick']
                if candle_1[body] == 'short' and candle_1['color'] == 'white':
                    basic_2 = day[2]['basic']
                    basic_1 = day[1]['basic']
                    if (basic_2['Close'] > basic_1['Open']) and (basic_2['Open'] > basic_1['Open']):
                        if basic_2['High'] > basic_1['High']:
                            candle_3 = day[3]['candlestick']
                            if candle_3[body] == 'short' and candle_3['color'] == 'white':
                                if day[3]['basic']['High'] > basic_2['High']:
                                    candle_4 = day[4]['candlestick']
                                    if candle_4[body] == 'long' and candle_4['color'] == 'black':
                                        basic_4 = day[4]['basic']
                                        if (basic_4['Close'] < basic_1['Open']) and \
                                                (basic_4['Close'] >= day[0]['basic']['Close']):
                                            return {"type": 'bearish', "style": 'breakaway -'}
    return None


def three_inside(day: list, body='body') -> dict:
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'short' and candle_1['color'] == 'white':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if (basic_1['Open'] > basic_0['Close']) and (basic_1['Close'] < basic_0['Open']):
                    if day[2]['candlestick']['color'] == 'white':
                        basic_2 = day[2]['basic']
                        if (basic_2['Open'] > basic_1['Open']) and \
                                (basic_2['Open'] < basic_1['Close']):
                            if (basic_2['Close'] > basic_0['Open']):
                                return {"type": 'bullish', "style": 'up'}

    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'short' and candle_1['color'] == 'black':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if (basic_1['Open'] < basic_0['Close']) and (basic_1['Close'] > basic_0['Open']):
                    if day[2]['candlestick']['color'] == 'black':
                        basic_2 = day[2]['basic']
                        if (basic_2['Open'] > basic_1['Close']) and \
                                (basic_2['Open'] < basic_1['Open']):
                            if (basic_2['Close'] < basic_0['Open']):
                                return {"type": 'bearish', "style": 'down'}
    return None


def three_outside(day: list, body='body') -> dict:
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0['color'] == 'black' and candle_0[body] != 'long':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'long' and candle_1['color'] == 'white':
                basic_1 = day[1]['basic']
                basic_0 = day[0]['basic']
                if (basic_0['Low'] > basic_1['Open']) and (basic_0['High'] < basic_1['Close']):
                    if day[2]['candlestick']['color'] == 'white':
                        basic_2 = day[2]['basic']
                        if (basic_2['Open'] > basic_1['Open']) and \
                            (basic_2['Open'] < basic_1['Close']) and \
                                (basic_2['Close'] > basic_2['Close']):
                            return {"type": 'bullish', "style": 'up'}

    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0['color'] == 'white' and candle_0[body] != 'long':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'long' and candle_1['color'] == 'black':
                basic_1 = day[1]['basic']
                basic_0 = day[0]['basic']
                if (basic_0['Low'] > basic_1['Close']) and (basic_0['High'] < basic_1['Open']):
                    if day[2]['candlestick']['color'] == 'black':
                        basic_2 = day[2]['basic']
                        if (basic_2['Open'] < basic_1['Open']) and \
                            (basic_2['Open'] > basic_1['Close']) and \
                                (basic_2['Close'] < basic_2['Close']):
                            return {"type": 'bearish', "style": 'down'}
    return None


def kicking(day: list, body='body') -> dict:
    THRESH = 0.01
    candle_0 = day[0]['candlestick']
    candle_1 = day[1]['candlestick']
    if candle_0[body] == 'long' and candle_0['color'] == 'black' and candle_1[body] == 'long' and \
            candle_1['color'] == 'white':
        basic_0 = day[0]['basic']
        oc_thr = np.abs(basic_0['Open'] - basic_0['Close']) * THRESH
        hi_op = basic_0['High'] - basic_0['Open']
        cl_lo = basic_0['Close'] - basic_0['Low']
        if (hi_op <= oc_thr) and (cl_lo <= oc_thr):
            basic_1 = day[1]['basic']
            oc_thr = np.abs(basic_1['Open'] - basic_1['Close']) * THRESH
            hi_cl = basic_1['High'] - basic_1['Close']
            op_lo = basic_1['Open'] - basic_1['Low']
            if (hi_cl <= oc_thr) and (op_lo <= oc_thr):
                if (basic_0['High'] < basic_1['Low']):
                    return {"type": 'bullish', "style": '+'}

    if candle_0[body] == 'long' and candle_0['color'] == 'white' and candle_1[body] == 'long' and \
            candle_1['color'] == 'black':
        basic_0 = day[0]['basic']
        oc_thr = np.abs(basic_0['Close'] - basic_0['Open']) * THRESH
        hi_op = basic_0['High'] - basic_0['Close']
        cl_lo = basic_0['Open'] - basic_0['Low']
        if (hi_op <= oc_thr) and (cl_lo <= oc_thr):
            basic_1 = day[1]['basic']
            oc_thr = np.abs(basic_1['Open'] - basic_1['Close']) * THRESH
            hi_cl = basic_1['High'] - basic_1['Open']
            op_lo = basic_1['Close'] - basic_1['Low']
            if (hi_cl <= oc_thr) and (op_lo <= oc_thr):
                if (basic_0['Low'] > basic_1['High']):
                    return {"type": 'bearish', "style": '-'}
    return None


def unique_three_river(day: list, body='body') -> dict:
    THRESH = 0.02
    SHADOW_RATIO = 2.0
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'short' and candle_1['color'] == 'black' and \
                    candle_1['shadow_ratio'] >= SHADOW_RATIO:
                basic_1 = day[1]['basic']
                basic_0 = day[0]['basic']
                hi_op = basic_1['High'] - basic_1['Open']
                oc_thr = (basic_1['Open'] - basic_1['Close']) * THRESH
                if (hi_op <= oc_thr) and (basic_1['Open'] < basic_0['Open']) and \
                        (basic_1['Low'] < basic_0['Close']):
                    if day[2]['candlestick']['color'] == 'white':
                        basic_2 = day[2]['basic']
                        if (basic_2['Open'] >= basic_0['Close']) and \
                                (basic_2['Close'] <= basic_1['Close']):
                            return {"type": 'bullish', "style": '+'}
    return None


def three_stars_in_the_south(day: list, body='body') -> dict:
    SHADOW_RATIO = 1.6
    OC_SHADOW_RATIO = 1.03
    THRESH = 0.01
    OP_THR = 0.2
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black' and \
                candle_0['shadow_ratio'] >= SHADOW_RATIO:
            basic_0 = day[0]['basic']
            hi_op = basic_0['High'] - basic_0['Open']
            oc_thr = np.abs(basic_0['Close'] - basic_0['Open']) * THRESH
            if (hi_op <= oc_thr):
                candle_1 = day[1]['candlestick']
                if candle_1[body] == 'short' and candle_1['color'] == 'black':
                    basic_1 = day[1]['basic']
                    op_point = (
                        (basic_0['Open'] - basic_0['Close']) * OP_THR) + basic_0['Close']
                    if (basic_1['Open'] < op_point) and \
                        (basic_1['Open'] > basic_0['Close']) and \
                            (basic_1['Close'] < basic_0['Close']) and \
                            (basic_1['Low'] > basic_0['Low']):
                        candle_2 = day[2]['candlestick']
                        if candle_2['shadow_ratio'] <= OC_SHADOW_RATIO and \
                                candle_2['color'] == 'black' and candle_2[body] == 'short':
                            basic_2 = day[2]['basic']
                            mid_pt = (
                                (basic_1['Open'] - basic_1['Close']) * 0.5) + basic_1['Close']
                            if basic_2['Open'] < mid_pt and basic_2['Close'] < basic_1['Close']:
                                return {"type": 'bullish', "style": "in the south +"}
    return None


def concealing_baby_swallow(day: list, body='body') -> dict:
    MF_SHADOW_RATIO = 1.03
    SHADOW_RATIO = 1.6
    THRESH = 0.02
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] != 'short' and candle_0['color'] == 'black' and \
                candle_0['shadow_ratio'] <= MF_SHADOW_RATIO:
            candle_1 = day[1]['candlestick']
            if candle_1[body] != 'short' and candle_1['color'] == 'black' and \
                    candle_1['shadow_ratio'] <= MF_SHADOW_RATIO:
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                mid_pt = ((basic_0['Open'] - basic_0['Close'])
                          * 0.5) + basic_0['Close']
                if (basic_1['Open'] < mid_pt) and (basic_1['Open'] >= basic_0['Close']):
                    candle_2 = day[2]['candlestick']
                    if candle_2[body] == 'short' and candle_2['color'] == 'black' and \
                            candle_2['shadow_ratio'] >= SHADOW_RATIO:
                        basic_2 = day[2]['basic']
                        oc_thr = (basic_2['Open'] - basic_2['Close']) * THRESH
                        cl_low = (basic_2['Close'] - basic_2['Low'])
                        if (cl_low <= oc_thr) and (basic_2['Open'] < basic_1['Close']) and \
                                (basic_2['High'] >= basic_1['Close']):
                            candle_3 = day[3]['candlestick']
                            if candle_3['color'] == 'black' and \
                                candle_3[body] != 'short' and \
                                    candle_3['shadow_ratio'] <= MF_SHADOW_RATIO:
                                basic_3 = day[3]['basic']
                                if (basic_3['Close'] <= basic_2['Close']) and \
                                        (basic_3['Open'] > basic_2['Open']):
                                    return {"type": 'bullish', "style": 'swallow +'}
    return None


def stick_sandwich(day: list, body='body') -> dict:
    THRESH = 0.02
    MF_SHADOW_RATIO = 1.03
    CLOSE_THRESH = 0.05
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            basic_0 = day[0]['basic']
            oc_thr = (basic_0['Open'] - basic_0['Close']) * THRESH
            cl_low = basic_0['Close'] - basic_0['Low']
            if (cl_low <= oc_thr):
                candle_1 = day[1]['candlestick']
                if candle_1[body] == 'long' and candle_1['color'] == 'white' and \
                        candle_1['shadow_ratio'] <= MF_SHADOW_RATIO:
                    basic_1 = day[1]['basic']
                    basic_0 = day[0]['basic']
                    if (basic_1['Open'] > basic_0['Close']) and \
                            (basic_1['Open'] < basic_0['Open']):
                        candle_2 = day[2]['candlestick']
                        if candle_2[body] == 'long' and candle_2['color'] == 'black':
                            basic_2 = day[2]['basic']
                            point1 = ((basic_2['Open'] - basic_2['Close']) * CLOSE_THRESH) + \
                                basic_2['Close']
                            point2 = basic_2['Close'] - \
                                ((basic_2['Open'] - basic_2['Close'])
                                 * CLOSE_THRESH)
                            if (basic_0['Close'] <= point1) and (basic_0['Close'] >= point2):
                                if basic_2['Open'] > basic_1['Close']:
                                    return {"type": 'bullish', "style": '+'}

    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            basic_0 = day[0]['basic']
            oc_thr = (basic_0['Close'] - basic_0['Open']) * THRESH
            cl_low = basic_0['High'] - basic_0['Close']
            if (cl_low <= oc_thr):
                candle_1 = day[1]['candlestick']
                if candle_1[body] == 'long' and candle_1['color'] == 'black' and \
                        candle_1['shadow_ratio'] <= MF_SHADOW_RATIO:
                    basic_1 = day[1]['basic']
                    basic_0 = day[0]['basic']
                    if (basic_1['Open'] > basic_0['Open']) and \
                            (basic_1['Open'] < basic_0['Close']):
                        candle_2 = day[2]['candlestick']
                        if candle_2[body] == 'long' and candle_2['color'] == 'white':
                            basic_2 = day[2]['basic']
                            point1 = ((basic_2['Close'] - basic_2['Open']) * CLOSE_THRESH) + \
                                basic_2['Close']
                            point2 = basic_2['Close'] - \
                                ((basic_2['Close'] - basic_2['Open'])
                                 * CLOSE_THRESH)
                            if (basic_0['Close'] <= point1) and (basic_0['Close'] >= point2):
                                if basic_2['Open'] < basic_1['Close']:
                                    return {"type": 'bearish', "style": '-'}
    return None


def identical_three_crows(day: list, body='body') -> dict:
    THRESH = 0.03
    SIZE_RANGE = 0.05
    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] != 'short' and candle_0['color'] == 'black':
            candle_1 = day[1]['candlestick']
            if candle_1[body] != 'short' and candle_1['color'] == 'black':
                basic_1 = day[1]['basic']
                basic_0 = day[0]['basic']
                point1 = ((basic_0['Open'] - basic_0['Close'])
                          * THRESH) + basic_0['Close']
                point2 = basic_0['Close'] - \
                    ((basic_0['Open'] - basic_0['Close']) * THRESH)
                if (basic_1['Open'] <= point1) and (basic_1['Close'] >= point2):
                    candle_2 = day[2]['candlestick']
                    if candle_2[body] != 'short' and candle_2['color'] == 'black':
                        basic_2 = day[2]['basic']
                        point1 = (
                            (basic_1['Open'] - basic_1['Close']) * THRESH) + basic_1['Close']
                        point2 = basic_1['Close'] - \
                            ((basic_1['Open'] - basic_1['Close']) * THRESH)
                        if (basic_2['Open'] <= point1) and (basic_2['Open'] >= point2):
                            length_0 = basic_0['Open'] - basic_0['Close']
                            upper_th = length_0 * (1.0 + SIZE_RANGE)
                            lower_th = length_0 * (1.0 - SIZE_RANGE)
                            length_1 = basic_1['Open'] - basic_1['Close']
                            length_2 = basic_2['Open'] - basic_2['Close']
                            if (length_1 <= upper_th) and (length_1 >= lower_th):
                                if (length_2 <= upper_th) and (length_2 >= lower_th):
                                    return {"type": 'bearish', "style": '-'}
    return None


def deliberation(day: list, body='body') -> dict:
    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'long' and candle_0['color'] == 'white':
                basic_0 = day[0]['basic']
                mid_pt = (basic_0['Close'] - basic_0['Open']) * 0.5
                basic_1 = day[1]['basic']
                if (basic_1['Open'] > mid_pt) and (basic_1['Open'] < basic_0['Close']) and \
                        (basic_1['Close'] > basic_0['Close']):
                    candle_2 = day[2]['candlestick']
                    if candle_2[body] == 'short' or candle_2['color'] == 'white':
                        basic_2 = day[2]['basic']
                        if (basic_2['Open'] > basic_1['Close']):
                            return {"type": 'bearish', "style": '-'}
    return None


def matching_high_low(day: list, body='body') -> dict:
    THRESH = 0.03
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            if day[1]['candlestick']['color'] == 'black':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                point1 = ((basic_0['Open'] - basic_0['Close'])
                          * THRESH) + basic_0['Close']
                point2 = basic_0['Close'] - \
                    ((basic_0['Open'] - basic_0['Close']) * THRESH)
                if (basic_1['Open'] < basic_0['Open']) and (basic_1['Close'] <= point1) and \
                        (basic_1['Close'] >= point2):
                    return {"type": 'bullish', "style": 'low'}

    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            if day[1]['candlestick']['color'] == 'white':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                point1 = ((basic_0['Close'] - basic_0['Open'])
                          * THRESH) + basic_0['Close']
                point2 = basic_0['Close'] - \
                    ((basic_0['Close'] - basic_0['Open']) * THRESH)
                if (basic_1['Open'] > basic_0['Open']) and (basic_1['Close'] <= point1) and \
                        (basic_1['Close'] >= point2):
                    return {"type": 'bearish', "style": 'high'}
    return None


def upside_gap_two_crows(day: list, body='body') -> dict:
    # Both upside_gap_two_crows and two_crows
    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'short' and candle_1['color'] == 'black':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if basic_1['Close'] > basic_0['Close']:
                    if day[1]['candlestick']['color'] == 'black':
                        basic_2 = day[2]['basic']
                        if (basic_2['Open'] >= basic_1['Open']) and \
                            (basic_2['Close'] <= basic_1['Close']) and \
                                (basic_2['Close'] > basic_0['Close']):
                            return {"type": 'bearish', "style": "upside_gap--"}
                        if (basic_2['Open'] > basic_1['Close']) and \
                            (basic_2['Open'] < basic_1['Open']) and \
                                (basic_2['Close'] < basic_1['Close']) and \
                                (basic_2['Close'] > basic_1['Open']):
                            return {"type": 'bearish', "style": '-'}
    return None


def homing_pigeon(day: list, body='body') -> dict:
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = day[1]['candlestick']
            if candle_1[body] != 'long' and candle_1['color'] == 'black':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if (basic_1['Open'] < basic_0['Open']) and (basic_1['Close'] > basic_0['Close']):
                    return {"type": 'bullish', "style": '+'}
    return None


def ladder(day: list, body='body') -> dict:
    SHADOW_RATIO = 2.0
    THRESH = 0.1
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] != 'short' and candle_0['color'] == 'black':
            candle_1 = day[1]['candlestick']
            basic_0 = day[0]['basic']
            basic_1 = day[1]['basic']
            if candle_1[body] != 'short' and candle_1['color'] == 'black' and \
                basic_1['Open'] < basic_0['Open'] and basic_1['Open'] > basic_0['Close'] and \
                    basic_1['Close'] < basic_0['Close']:
                candle_2 = day[2]['candlestick']
                basic_2 = day[2]['basic']
                if candle_2[body] != 'short' and candle_2['color'] == 'black' and \
                    basic_2['Open'] < basic_1['Open'] and \
                        basic_2['Open'] > basic_1['Close'] and \
                        basic_2['Close'] < basic_1['Close']:
                    candle_3 = day[3]['candlestick']
                    if candle_3[body] == 'short' and candle_3['color'] == 'black' and \
                            candle_3['shadow_ratio'] >= SHADOW_RATIO:
                        basic_3 = day[3]['basic']
                        oc_thr = (basic_3['Open'] - basic_3['Close']) * THRESH
                        cl_low = basic_3['Close'] - basic_3['Low']
                        if (basic_3['Close'] < basic_2['Close']) and (cl_low <= oc_thr):
                            candle_4 = day[4]['candlestick']
                            if candle_4[body] == 'long' and candle_4['color'] == 'white' and \
                                    day[4]['basic']['Open'] > basic_3['Open']:
                                return {"type": 'bullish', "style": 'bottom +'}
    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] != 'short' and candle_0['color'] == 'white':
            candle_1 = day[1]['candlestick']
            basic_0 = day[0]['basic']
            basic_1 = day[1]['basic']
            if candle_1[body] != 'short' and candle_1['color'] == 'white' and \
                basic_1['Open'] > basic_0['Open'] and basic_1['Open'] < basic_0['Close'] and \
                    basic_1['Close'] > basic_0['Close']:
                candle_2 = day[2]['candlestick']
                basic_2 = day[2]['basic']
                if candle_2[body] != 'short' and candle_2['color'] == 'white' and \
                    basic_2['Open'] > basic_1['Open'] and \
                        basic_2['Open'] < basic_1['Close'] and \
                        basic_2['Close'] > basic_1['Close']:
                    candle_3 = day[3]['candlestick']
                    if candle_3[body] == 'short' and candle_3['color'] == 'white' and \
                            candle_3['shadow_ratio'] >= SHADOW_RATIO:
                        basic_3 = day[3]['basic']
                        oc_thr = (basic_3['Open'] - basic_3['Close']) * THRESH
                        cl_low = basic_3['High'] - basic_3['Close']
                        if (basic_3['Close'] > basic_2['Close']) and (cl_low <= oc_thr):
                            candle_4 = day[4]['candlestick']
                            if candle_4['body'] == 'long' and candle_4['color'] == 'black' and \
                                    day[4]['basic']['Open'] < basic_3['Open']:
                                return {"type": 'bearish', "style": 'top -'}
    return None


def advance_block(day: list, body='body') -> dict:
    if day[0]['trend'] == 'above':
        if day[0]['candlestick']['color'] == 'white':
            basic_0 = day[0]['basic']
            basic_1 = day[1]['basic']
            if basic_1['Open'] > basic_0['Open'] and basic_1['Open'] < basic_0['Close'] and \
                    basic_1['Close'] > basic_0['Close'] and day[1]['candlestick']['color'] == 'white':
                candle_2 = day[2]['candlestick']
                if candle_2[body] == 'short' and candle_2['color'] == 'white':
                    basic_2 = day[2]['basic']
                    if basic_2['Open'] > basic_1['Open'] and \
                        basic_2['Open'] < basic_1['Close'] and \
                            basic_2['Close'] > basic_1['Close']:
                        return {"type": 'bearish', "style": '-'}
    return None


def separating_lines(day: list, body='body') -> dict:
    THRESH = 0.05
    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'long' and candle_1['color'] == 'white':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                oc_thr = np.abs(basic_0['Open'] - basic_0['Close']) * THRESH
                point1 = basic_0['Open'] - oc_thr
                point2 = basic_0['Open'] + oc_thr
                if basic_1['Open'] <= point2 and basic_1['Open'] >= point1:
                    return {"type": 'bullish', "style": '+'}

    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            candle_1 = day[1]['candlestick']
            if candle_1[body] == 'long' and candle_1['color'] == 'black':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                oc_thr = np.abs(basic_0['Close'] - basic_0['Open']) * THRESH
                point1 = basic_0['Open'] - oc_thr
                point2 = basic_0['Open'] + oc_thr
                if basic_1['Open'] <= point2 and basic_1['Open'] >= point1:
                    return {"type": 'bearish', "style": '-'}

    return None


def tasuki_gap_upside_downside(day: list, body='body') -> dict:
    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            if day[1]['candlestick']['color'] == 'white':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if basic_1['Low'] > basic_0['High']:
                    if day[2]['candlestick']['color'] == 'black':
                        basic_2 = day[2]['basic']
                        if basic_2['Open'] <= basic_1['Close'] and \
                                basic_2['Open'] >= basic_1['Open']:
                            if basic_2['Close'] < basic_1['Open'] and \
                                    basic_2['Close'] > basic_0['Close']:
                                return {"type": 'bullish', "style": 'upside +'}

    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            if day[1]['candlestick']['color'] == 'black':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if basic_0['Low'] > basic_1['High']:
                    if day[2]['candlestick']['color'] == 'white':
                        basic_2 = day[2]['basic']
                        if basic_2['Open'] <= basic_1['Open'] and \
                                basic_2['Open'] >= basic_1['Close']:
                            if basic_2['Close'] > basic_1['Open'] and \
                                    basic_2['Close'] < basic_0['Close']:
                                return {"type": 'bearish', "style": 'downside -'}
    return None


def side_by_side_white_lines(day: list, body='body') -> dict:
    THRESH = 0.1
    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            if day[1]['candlestick']['color'] == 'white':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if basic_1['Low'] > basic_0['High']:
                    if day[2]['candlestick']['color'] == 'white':
                        basic_2 = day[2]['basic']
                        oc_thr = (basic_1['Close'] - basic_1['Open']) * THRESH
                        point1 = basic_1['Open'] - oc_thr
                        point2 = basic_1['Open'] + oc_thr
                        if basic_2['Low'] > basic_0['High'] and basic_2['Open'] >= point1 and \
                                basic_2['Open'] <= point2 and basic_2['Close'] <= basic_1['Close']:
                            return {"type": 'bullish', "style": 'white lines +'}

    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            if day[1]['candlestick']['color'] == 'white':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if basic_1['High'] < basic_0['Low']:
                    if day[2]['candlestick']['color'] == 'white':
                        basic_2 = day[2]['basic']
                        oc_thr = (basic_1['Close'] - basic_1['Open']) * THRESH
                        point1 = basic_1['Open'] - oc_thr
                        point2 = basic_1['Open'] + oc_thr
                        if basic_2['High'] < basic_0['Low'] and basic_2['Open'] >= point1 and \
                                basic_2['Open'] <= point2 and basic_2['Close'] <= basic_1['Close']:
                            return {"type": 'bearish', "style": 'white lines -'}

    return None


def three_line_strike(day: list, body='body') -> dict:
    if day[0]['trend'] == 'below':
        if day[0]['candlestick']['color'] == 'black' and day[1]['candlestick']['color'] == 'black' \
                and day[2]['candlestick']['color'] == 'black':
            basic_0 = day[0]['basic']
            basic_1 = day[1]['basic']
            if basic_1['Open'] < basic_0['Open'] and basic_1['Close'] < basic_0['Close']:
                basic_2 = day[2]['basic']
                if basic_2['Open'] < basic_1['Open'] and basic_2['Close'] < basic_1['Close']:
                    if day[3]['candlestick']['color'] == 'white':
                        basic_3 = day[3]['basic']
                        if basic_3['Open'] <= basic_2['Close'] and \
                                basic_3['Close'] >= basic_0['Open']:
                            return {"type": 'bearish', "style": '-'}

    if day[0]['trend'] == 'above':
        if day[0]['candlestick']['color'] == 'white' and day[1]['candlestick']['color'] == 'white' \
                and day[2]['candlestick']['color'] == 'white':
            basic_0 = day[0]['basic']
            basic_1 = day[1]['basic']
            if basic_1['Open'] > basic_0['Open'] and basic_1['Close'] > basic_0['Close']:
                basic_2 = day[2]['basic']
                if basic_2['Open'] > basic_1['Open'] and basic_2['Close'] > basic_1['Close']:
                    if day[3]['candlestick']['color'] == 'black':
                        basic_3 = day[3]['basic']
                        if basic_3['Open'] >= basic_2['Close'] and \
                                basic_3['Close'] <= basic_0['Open']:
                            return {"type": 'bullish', "style": '+'}
    return None


def upside_downside_gap_three_methods(day: list, body='body') -> dict:
    if day[0]['trend'] == 'below':
        if day[0]['candlestick']['color'] == 'black' and day[1]['candlestick']['color'] == 'black':
            basic_0 = day[0]['basic']
            basic_1 = day[1]['basic']
            if basic_1['High'] < basic_0['Low'] and day[2]['candlestick']['color'] == 'white':
                basic_2 = day[2]['basic']
                if basic_2['Open'] < basic_1['Open'] and basic_2['Open'] > basic_1['Close'] and \
                        basic_2['Close'] > basic_0['Close'] and basic_2['Close'] < basic_2['Open']:
                    return {"type": 'bearish', "style": 'downside -'}

    if day[0]['trend'] == 'above':
        if day[0]['candlestick']['color'] == 'white' and day[1]['candlestick']['color'] == 'white':
            basic_0 = day[0]['basic']
            basic_1 = day[1]['basic']
            if basic_1['Low'] > basic_0['High'] and day[2]['candlestick']['color'] == 'black':
                basic_2 = day[2]['basic']
                if basic_2['Open'] < basic_1['Close'] and basic_2['Open'] > basic_1['Open'] and \
                        basic_2['Close'] > basic_0['Open'] and basic_2['Close'] < basic_2['Close']:
                    return {"type": 'bullish', "style": 'upside +'}
    return None


def on_in_neck_line(day: list, body='body') -> dict:
    THRESH = 0.05
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'black':
            if day[1]['candlestick']['color'] == 'white':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if basic_1['Open'] < basic_0['Low']:
                    oc_thr = (basic_0['Open'] - basic_0['Close']) * THRESH
                    point1 = basic_0['Close'] - oc_thr
                    point2 = basic_0['Close'] + oc_thr
                    if basic_1['Close'] >= point1 and basic_1['Close'] <= point2:
                        return {"type": 'bearish', "style": 'in -'}
                    if basic_1['Close'] <= basic_0['Close'] and basic_1['Close'] >= basic_0['Low']:
                        return {"type": 'bearish', "style": 'on -'}

    if day[0]['trend'] == 'above':
        candle_0 = day[0]['candlestick']
        if candle_0[body] == 'long' and candle_0['color'] == 'white':
            if day[1]['candlestick']['color'] == 'black':
                basic_0 = day[0]['basic']
                basic_1 = day[1]['basic']
                if basic_1['Open'] > basic_0['High']:
                    oc_thr = (basic_0['Close'] - basic_0['Open']) * THRESH
                    point1 = basic_0['Close'] - oc_thr
                    point2 = basic_0['Close'] + oc_thr
                    if basic_1['Close'] >= point1 and basic_1['Close'] <= point2:
                        return {"type": 'bullish', "style": 'in +'}
                    if basic_1['Close'] >= basic_0['Close'] and basic_1['Close'] <= basic_0['High']:
                        return {"type": 'bullish', "style": 'on +'}
    return None


PATTERNS = {
    "doji": {'days': 1, 'function': doji_pattern},
    "dark cloud piercing line": {'days': 2, 'function': dark_cloud_or_piercing_line},
    "evening morning star": {'days': 3, 'function': evening_morning_star},
    "three methods": {'days': 5, 'function': rising_falling_three_methods},
    "hammer": {'days': 1, 'function': hammer_positive},
    "hanging man": {'days': 1, 'function': hanging_man},
    "inverted hammer": {'days': 2, 'function': inverted_hammer},
    "shooting star": {'days': 2, 'function': shooting_star},
    "belt hold": {'days': 1, 'function': belt_hold},
    "engulfing": {'days': 2, 'function': engulfing},
    "harami": {'days': 2, 'function': harami},
    "doji star": {'days': 2, 'function': doji_star},
    "meeting line": {'days': 2, 'function': meeting_line},
    "three soldier crows": {'days': 3, 'function': three_white_soldiers_black_crows},
    "tri star": {'days': 3, 'function': tri_star, "weight": 3},
    "breakaway": {'days': 5, 'function': breakaway},
    "three inside": {'days': 3, 'function': three_inside},
    "three outside": {'days': 3, 'function': three_outside},
    "kicking": {'days': 2, 'function': kicking},
    "three river": {'days': 3, 'function': unique_three_river},
    "three stars": {'days': 3, 'function': three_stars_in_the_south},
    "concealing baby": {'days': 4, 'function': concealing_baby_swallow},
    "stick sandwich": {'days': 3, 'function': stick_sandwich},
    "identical crows": {'days': 3, 'function': identical_three_crows},
    "deliberation": {'days': 3, 'function': deliberation},
    "matching": {'days': 2, 'function': matching_high_low},
    "two crows": {'days': 3, 'function': upside_gap_two_crows},
    "homing pigeon": {'days': 2, 'function': homing_pigeon},
    "ladder": {'days': 5, 'function': ladder},
    "advance block": {'days': 3, 'function': advance_block},
    "separating lines": {'days': 2, 'function': separating_lines},
    "tasuki gap": {'days': 3, 'function': tasuki_gap_upside_downside},
    "side by side": {'days': 3, 'function': side_by_side_white_lines},
    "three line strike": {'days': 4, 'function': three_line_strike},
    "gap three methods": {'days': 3, 'function': upside_downside_gap_three_methods},
    "neck line": {'days': 2, 'function': on_in_neck_line}
}
