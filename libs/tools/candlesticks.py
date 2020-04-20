import pprint
from copy import deepcopy
import pandas as pd
import numpy as np

from libs.utils import ProgressBar
from libs.utils import candlestick
from .moving_average import simple_moving_avg
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
    candle['classification'] = day_classification(fund, candle['thresholds'])
    candle = pattern_detection(fund, candle)

    if plot_output:
        candlestick(fund, title=name)
    else:
        filename = f"{name}/{view}/candlestick_{name}"
        candlestick(fund, title=name, filename=filename,
                    saveFig=True)

    if pbar is not None:
        pbar.uptick(increment=1.0)
    return candle


def pattern_detection(fund: pd.DataFrame, candle: dict, **kwargs) -> dict:
    """Pattern Detection

    Searches available candlestick patterns on each area of the dataset

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        candle {dict} -- candlestick data object

    Returns:
        dict -- candlestick data object
    """
    plot_output = kwargs.get('plot_output', True)

    patterns = []
    for i in range(len(candle['classification'])):
        value = {'value': 0, 'patterns': []}
        for patt in PATTERNS:
            val = pattern_library(patt, candle['classification'], i)
            if val[0] != 0:
                value['value'] += val[0]
                modified_pattern = f"{patt}-{val[1]}"
                value['patterns'].append(modified_pattern)
        patterns.append(value)

    patterns2 = filtered_reversal_patterns(fund, candle)

    for i, patt in enumerate(patterns2):
        if patt['value'] != 0:
            patterns[i]['value'] += patt['value']
            patterns[i]['patterns'].extend(patt['patterns'])

    signal = simple_moving_avg(fund, 10)
    for i, patt in enumerate(patterns):
        if patt['value'] != 0:
            signal[i] += (patt['value'] * 10.0)
            print(f"index {i}: {patt['value']} => {patt['patterns']}")

    if plot_output:
        plot_obj = {"plot": signal, "color": 'black',
                    "legend": 'candlestick signal'}
        candlestick(fund, additional_plts=[
                    plot_obj], title='Candlestick Signals')

    candle['patterns'] = patterns
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

    thresholds = dict()
    thresholds['short'] = np.percentile(open_close, SHORT)
    thresholds['long'] = np.percentile(open_close, LONG)
    thresholds['doji'] = np.percentile(open_close, DOJI)
    thresholds['doji_ratio'] = DOJI_RATIO

    if plot_output:
        print(f"\r\nThresholding for candlesticks:")
        pprint.pprint(thresholds)
        candlestick(fund, title="Doji & Long/Short Days",
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
            modified_pattern = f"dark_cloud_piercing_line-{val[1]}"
            value['patterns'].append(modified_pattern)

        val = pattern_library("evening_morning_star",
                              candle['classification'], i)
        if val[0] != 0:
            value['value'] += val[0]
            modified_pattern = f"evening_morning_star-{val[1]}"
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

def pattern_library(pattern: str, days: list, index: int) -> list:
    """Pattern Library

    Command function for properly configuring and running various pattern detections.

    Arguments:
        pattern {str} -- key from PATTERNS object
        days {list} -- candle objects generated from day_classification
        index {int} -- index of DataFrame or list

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

    detection = function(sub_days)
    if detection is not None:
        if detection['type'] == 'bearish':
            return -1 * weight, detection['style']
        if detection['type'] == 'bullish':
            return 1 * weight, detection['style']

    return 0, ''


###################################

def doji_pattern(day: list) -> dict:
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


def dark_cloud_or_piercing_line(day: list) -> dict:
    # Dark Cloud
    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('body') == 'long':
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
        if candle_0.get('body') == 'long':
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
                        return {'type': 'bullish', 'style': 'piercingline'}

    return None


def evening_morning_star(day: list) -> dict:
    # Evening star
    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('body') == 'long':
            if candle_0.get('color') == 'white':
                basic_0 = day[0].get('basic')
                basic_1 = day[1].get('basic')
                close_0 = basic_0.get('Close')
                open_1 = basic_1.get('Open')
                if open_1 > close_0:
                    candle_1 = day[1].get('candlestick')
                    if candle_1.get('body') == 'short':
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
                                            return {"type": 'bearish', "style": 'abandonedbaby--'}
                                        return {"type": 'bearish', "style": 'eveningstar-doji'}
                                    return {'type': 'bearish', 'style': 'eveningstar'}

    # Morning star
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('body') == 'long':
            if candle_0.get('color') == 'black':
                basic_0 = day[0].get('basic')
                basic_1 = day[1].get('basic')
                close_0 = basic_0.get('Close')
                open_1 = basic_1.get('Open')
                if open_1 < close_0:
                    candle_1 = day[1].get('candlestick')
                    if candle_1.get('body') == 'short':
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
                                            return {"type": 'bullish', "style": 'abandonedbaby-+'}
                                        return {"type": 'bullish', "style": 'morningstar-doji'}
                                    return {'type': 'bullish', 'style': 'morningstar'}

    return None


def rising_falling_three_methods(day: list) -> dict:
    # Rising three methods (continuation of bull trend)
    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('body') == 'long':
            if candle_0.get('color') == 'white':
                basic_0 = day[0].get('basic')
                high_0 = basic_0.get('High')
                low_0 = basic_0.get('Low')
                close_0 = basic_0.get('Close')
                basic_1 = day[1].get('basic')
                if high_0 >= max(basic_1.get('Open'), basic_1.get('Close')):
                    if low_0 <= min(basic_1.get('Open'), basic_1.get('Close')):
                        if day[1].get('candlestick').get('body') == 'short':
                            basic_2 = day[1].get('basic')
                            if high_0 >= max(basic_2.get('Open'), basic_2.get('Close')):
                                if low_0 <= min(basic_2.get('Open'), basic_2.get('Close')):
                                    basic_3 = day[1].get('basic')
                                    if high_0 >= max(basic_3.get('Open'), basic_3.get('Close')):
                                        if low_0 <= min(basic_3.get('Open'), basic_3.get('Close')):
                                            candle_4 = day[4].get(
                                                'candlestick')
                                            if candle_4.get('body') == 'long':
                                                if candle_4.get('color') == 'white':
                                                    if day[4].get('basic', {}).get('Close') > close_0:
                                                        return {"type": 'bullish',
                                                                "style": 'risingthreemethods'}

    # Falling three methods (continuation of bear trend)
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('body') == 'long':
            if candle_0.get('color') == 'black':
                basic_0 = day[0].get('basic')
                high_0 = basic_0.get('High')
                low_0 = basic_0.get('Low')
                close_0 = basic_0.get('Close')
                basic_1 = day[1].get('basic')
                if low_0 <= min(basic_1.get('Open'), basic_1.get('Close')):
                    if high_0 >= max(basic_1.get('Open'), basic_1.get('Close')):
                        if day[1].get('candlestick').get('body') == 'short':
                            basic_2 = day[1].get('basic')
                            if low_0 <= min(basic_2.get('Open'), basic_2.get('Close')):
                                if high_0 >= max(basic_2.get('Open'), basic_2.get('Close')):
                                    basic_3 = day[1].get('basic')
                                    if low_0 <= min(basic_3.get('Open'), basic_3.get('Close')):
                                        if high_0 >= max(basic_3.get('Open'), basic_3.get('Close')):
                                            candle_4 = day[4].get(
                                                'candlestick')
                                            if candle_4.get('body') == 'long':
                                                if candle_4.get('color') == 'black':
                                                    if day[4].get('basic', {}).get('Close') < close_0:
                                                        return {"type": 'bearish',
                                                                "style": 'fallingthreemethods'}

    return None


def hammer_positive(day: list) -> dict:
    RATIO = 2.0
    THRESH = 0.99
    if day[0].get('trend') == 'below':
        candle = day[0].get('candlestick')
        if candle.get('body') == 'short':
            if candle.get('shadow_ratio') >= RATIO:
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


def hanging_man(day: list) -> dict:
    RATIO = 2.0
    THRESH = 0.99
    if day[0].get('trend') == 'above':
        candle = day[0].get('candlestick')
        if candle.get('body') == 'short':
            if candle.get('shadow_ratio') >= RATIO:
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


def inverted_hammer(day: list) -> dict:
    RATIO = 2.0
    THRESH = 0.01
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('body') == 'long':
            if candle_0.get('color') == 'black':
                candle_1 = day[1].get('candlestick')
                if candle_1.get('body') == 'short':
                    if candle_1.get('shadow_ratio') >= RATIO:
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


def shooting_star(day: list) -> dict:
    RATIO = 2.0
    THRESH = 0.01
    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('body') == 'long':
            if candle_0.get('color') == 'white':
                basic_0 = day[0].get('basic')
                if basic_0.get('Close') < basic_0.get('High'):
                    candle_1 = day[1].get('candlestick')
                    if candle_1.get('body') == 'short':
                        if candle_1.get('shadow_ratio') >= RATIO:
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


def belt_hold(day: list) -> dict:
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


def engulfing(day: list) -> dict:
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'black':
            candle_1 = day[1].get('candlestick')
            if candle_1.get('body') == 'long':
                if candle_1.get('color') == 'white':
                    basic_0 = day[0].get('basic')
                    basic_1 = day[1].get('basic')
                    if basic_0.get('High') <= basic_1.get('Close'):
                        if basic_0.get('Low') >= basic_1.get('Open'):
                            return {"type": 'bullish', "style": '+'}

    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'white':
            candle_1 = day[1].get('candlestick')
            if candle_1.get('body') == 'long':
                if candle_1.get('color') == 'black':
                    basic_0 = day[0].get('basic')
                    basic_1 = day[1].get('basic')
                    if basic_0.get('High') <= basic_1.get('Open'):
                        if basic_0.get('Low') >= basic_1.get('Close'):
                            return {"type": 'bearish', "style": '-'}
    return None


def harami(day: list) -> dict:
    THRESH = 0.01
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'black':
            if candle_0.get('body') == 'long':
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
        if candle_0.get('color') == 'white':
            if candle_0.get('body') == 'long':
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


def doji_star(day: list) -> dict:
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'black':
            if candle_0.get('body') != 'short':
                basic_1 = day[1].get('basic')
                basic_0 = day[0].get('basic')
                if basic_1.get('High') <= basic_0.get('Close'):
                    candle_1 = day[1].get('candlestick')
                    if candle_1.get('doji'):
                        return {"type": 'bullish', "style": "+"}

    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'white':
            if candle_0.get('body') != 'short':
                basic_1 = day[1].get('basic')
                basic_0 = day[0].get('basic')
                if basic_1.get('Low') >= basic_0.get('Close'):
                    candle_1 = day[1].get('candlestick')
                    if candle_1.get('doji'):
                        return {"type": 'bearish', "style": "-"}
    return None


def meeting_line(day: list) -> dict:
    THRESH = 0.01
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('body') != 'short':
            if candle_0.get('color') == 'black':
                candle_1 = day[1].get('candlestick')
                if candle_1.get('color') == 'white':
                    if candle_1.get('body') != 'short':
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
        if candle_0.get('body') != 'short':
            if candle_0.get('color') == 'white':
                candle_1 = day[1].get('candlestick')
                if candle_1.get('color') == 'black':
                    if candle_1.get('body') != 'short':
                        basic_1 = day[1].get('basic')
                        basic_0 = day[0].get('basic')
                        hl_thr = (basic_1.get('High') -
                                  basic_1.get('Low')) * THRESH
                        cl_cl = np.abs(basic_0.get('Close') -
                                       basic_1.get('Close'))
                        if cl_cl <= hl_thr:
                            return {"type": 'bearish', "style": "-"}
    return None


def three_white_soldiers_black_crows(day: list) -> dict:
    THRESH = 0.3
    if day[0].get('trend') == 'below':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'white':
            if candle_0.get('body') != 'short':
                candle_1 = day[1].get('candlestick')
                if (candle_1.get('color') == 'white') and (candle_1.get('body') != 'short'):
                    basic_0 = day[0].get('basic')
                    basic_1 = day[1].get('basic')
                    body_th = ((basic_0.get('Close') - basic_0.get('Open'))
                               * THRESH) + basic_0.get('Open')
                    if (basic_1.get('Open') > body_th) and (basic_1['Close'] > basic_0['Close']) \
                            and (basic_1['Open'] < basic_0['Close']):
                        candle_2 = day[2].get('candlestick')
                        if (candle_2['color'] == 'white') and (candle_2['body'] != 'short'):
                            basic_2 = day[2].get('basic')
                            body_th = (
                                (basic_1['Close'] - basic_1['Open']) * THRESH) + basic_1['Open']
                            if (basic_2['Open'] > body_th) and (basic_2['Close'] > basic_1['Close']) \
                                    and (basic_2['Open'] < basic_1['Close']):
                                return {"type": 'bullish', "style": 'white_soldiers'}

    if day[0].get('trend') == 'above':
        candle_0 = day[0].get('candlestick')
        if candle_0.get('color') == 'black':
            if candle_0.get('body') != 'short':
                candle_1 = day[1].get('candlestick')
                if (candle_1.get('color') == 'black') and (candle_1.get('body') != 'short'):
                    basic_0 = day[0].get('basic')
                    basic_1 = day[1].get('basic')
                    body_th = ((basic_0.get('Close') - basic_0.get('Open'))
                               * (1.0 - THRESH)) + basic_0.get('Open')
                    if (basic_1.get('Open') < body_th) and (basic_1['Close'] < basic_0['Close']) \
                            and (basic_1['Open'] > basic_0['Close']):
                        candle_2 = day[2].get('candlestick')
                        if (candle_2['color'] == 'black') and (candle_2['body'] != 'short'):
                            basic_2 = day[2].get('basic')
                            body_th = (
                                (basic_1['Close'] - basic_1['Open']) * (1.0 - THRESH)) + basic_1['Open']
                            if (basic_2['Open'] < body_th) and \
                                (basic_2['Close'] < basic_1['Close']) and \
                                    (basic_2['Open'] > basic_1['Close']):
                                return {"type": 'bearish', "style": 'black_crows'}
    return None


def tri_star(day: list) -> dict:
    if day[0]['trend'] == 'below':
        if day[0]['candlestick']['doji'] and \
            day[1]['candlestick']['doji'] and \
                day[2]['candlestick']['doji']:
            if day[1]['basic']['Close'] < day[0]['basic']['Close']:
                if day[1]['basic']['Close'] < day[2]['basic']['Close']:
                    return {"type": 'bullish', "style": 'tristar-+'}

    if day[0]['trend'] == 'above':
        if day[0]['candlestick']['doji'] and \
            day[1]['candlestick']['doji'] and \
                day[2]['candlestick']['doji']:
            if day[1]['basic']['Close'] > day[0]['basic']['Close']:
                if day[1]['basic']['Close'] > day[2]['basic']['Close']:
                    return {"type": 'bearish', "style": 'tristar--'}
    return None


def breakaway(day: list) -> dict:
    if day[0]['trend'] == 'below':
        if (day[0]['candlestick']['body'] == 'long') and \
                (day[0]['candlestick']['color'] == 'black'):
            if day[0]['basic']['Low'] > day[1]['basic']['High']:
                candle_1 = day[1]['candlestick']
                if (candle_1['body'] == 'short') and (candle_1['color'] == 'black'):
                    basic_2 = day[2]['basic']
                    basic_1 = day[1]['basic']
                    if (basic_2['Close'] < basic_1['Open']) and (basic_2['Open'] < basic_1['Open']):
                        if basic_2['Low'] < basic_1['Low']:
                            candle_3 = day[3]['candlestick']
                            if (candle_3['body'] == 'short') and (candle_3['color'] == 'black'):
                                if day[3]['basic']['Low'] < basic_2['Low']:
                                    candle_4 = day[4]['candlestick']
                                    if (candle_4['body'] == 'long') and \
                                            (candle_4['color'] == 'white'):
                                        basic_4 = day[4]['basic']
                                        if (basic_4['Close'] > basic_1['Open']) and \
                                                (basic_4['Close'] <= day[0]['basic']['Close']):
                                            return {"type": 'bullish', "style": 'breakaway-+'}

    if day[0]['trend'] == 'above':
        if (day[0]['candlestick']['body'] == 'long') and \
                (day[0]['candlestick']['color'] == 'white'):
            if day[0]['basic']['High'] < day[1]['basic']['Low']:
                candle_1 = day[1]['candlestick']
                if (candle_1['body'] == 'short') and (candle_1['color'] == 'white'):
                    basic_2 = day[2]['basic']
                    basic_1 = day[1]['basic']
                    if (basic_2['Close'] > basic_1['Open']) and (basic_2['Open'] > basic_1['Open']):
                        if basic_2['High'] > basic_1['High']:
                            candle_3 = day[3]['candlestick']
                            if (candle_3['body'] == 'short') and (candle_3['color'] == 'white'):
                                if day[3]['basic']['High'] > basic_2['High']:
                                    candle_4 = day[4]['candlestick']
                                    if (candle_4['body'] == 'long') and \
                                            (candle_4['color'] == 'black'):
                                        basic_4 = day[4]['basic']
                                        if (basic_4['Close'] < basic_1['Open']) and \
                                                (basic_4['Close'] >= day[0]['basic']['Close']):
                                            return {"type": 'bearish', "style": 'breakaway--'}
    return None


def three_inside(day: list) -> dict:
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if (candle_0['body'] == 'long') and (candle_0['color'] == 'black'):
            candle_1 = day[1]['candlestick']
            if (candle_1['body'] == 'short') and (candle_1['color'] == 'white'):
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
        if (candle_0['body'] == 'long') and (candle_0['color'] == 'white'):
            candle_1 = day[1]['candlestick']
            if (candle_1['body'] == 'short') and (candle_1['color'] == 'black'):
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


def three_outside(day: list) -> dict:
    if day[0]['trend'] == 'below':
        candle_0 = day[0]['candlestick']
        if (candle_0['color'] == 'black') and (candle_0['body'] != 'long'):
            candle_1 = day[1]['candlestick']
            if (candle_1['body'] == 'long') and (candle_1['color'] == 'white'):
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
        if (candle_0['color'] == 'white') and (candle_0['body'] != 'long'):
            candle_1 = day[1]['candlestick']
            if (candle_1['body'] == 'long') and (candle_1['color'] == 'black'):
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


PATTERNS = {
    "doji": {'days': 1, 'function': doji_pattern},
    "dark_cloud_piercing_line": {'days': 2, 'function': dark_cloud_or_piercing_line},
    "evening_morning_star": {'days': 3, 'function': evening_morning_star},
    "three_methods": {'days': 5, 'function': rising_falling_three_methods},
    "hammer": {'days': 1, 'function': hammer_positive},
    "hanging_man": {'days': 1, 'function': hanging_man},
    "inverted_hammer": {'days': 2, 'function': inverted_hammer},
    "shooting_star": {'days': 2, 'function': shooting_star},
    "belt_hold": {'days': 1, 'function': belt_hold},
    "engulfing": {'days': 2, 'function': engulfing},
    "harami": {'days': 2, 'function': harami},
    "doji_star": {'days': 2, 'function': doji_star},
    "meeting_line": {'days': 2, 'function': meeting_line},
    "three_soldier_crows": {'days': 3, 'function': three_white_soldiers_black_crows},
    "tri_star": {'days': 3, 'function': tri_star, "weight": 3},
    "breakaway": {'days': 5, 'function': breakaway},
    "three_inside": {'days': 3, 'function': three_inside},
    "three_outside": {'days': 3, 'function': three_outside}
}
