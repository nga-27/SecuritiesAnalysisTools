import os
from typing import Tuple, List

import pandas as pd
import numpy as np

from libs.utils import INDEXES, generate_plot, PlotType
from libs.utils.plot_utils import utils

from .moving_average import simple_moving_avg, exponential_moving_avg
from .moving_average import adjust_signals
from .full_stochastic import generate_full_stoch_signal

from .candlestick_patterns import (
    doji_pattern, dark_cloud_or_piercing_line, neckline, three_methods, three_line_strike,
    side_by_side, tasuki_gap, separating_lines, advanced_block, ladder, homing_pigeon, two_crows,
    matching, deliberation, identical_crows, stick_sandwich, concealing_baby, three_stars,
    three_river
)


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

    candles = {}

    candles['thresholds'] = determine_threshold(fund, plot_output=plot_output)
    if pbar is not None:
        pbar.uptick(increment=0.1)

    candles['classification'] = day_classification(fund, candles['thresholds'])
    if pbar is not None:
        pbar.uptick(increment=0.1)

    candles = pattern_detection(
        fund, candles, plot_output=plot_output, pbar=pbar)

    candles['signals'] = get_pattern_signals(candles, fund)
    candles['length_of_data'] = len(fund.index)

    fifty_day = simple_moving_avg(fund, 50)
    fifty_day_x, fifty_day = adjust_signals(fund, fifty_day, offset=50)

    two_hundred_day = simple_moving_avg(fund, 200)
    two_hundred_day_x, two_hundred_day = adjust_signals(
        fund, two_hundred_day, offset=200)

    plot_50 = {"plot": fifty_day, "color": "blue",
               "legend": "50-day MA", "x": fifty_day_x}
    plot_200 = {"plot": two_hundred_day,
                "color": "black", "legend": "200-day MA", "x": two_hundred_day_x}

    name2 = INDEXES.get(name, name)

    generate_plot(
        PlotType.CANDLESTICKS,
        fund,
        **{
            "title": name2,
            "additional_plots": [plot_50, plot_200],
            "plot_output": plot_output,
            "filename": os.path.join(name, view, f"candlestick_{name}.png")
        }
    )

    if pbar is not None:
        pbar.uptick(increment=0.1)
    return candles


def pattern_detection(fund: pd.DataFrame, candles: dict, **kwargs) -> dict:
    """Pattern Detection

    Searches available candlestick patterns on each area of the dataset

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        candles {dict} -- candlestick data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        pbar {ProgressBar} -- (default: {None})

    Returns:
        dict -- candlestick data object
    """
    plot_output = kwargs.get('plot_output', True)
    pbar = kwargs.get('pbar')

    if pbar is not None:
        divisor = 0.7 / float(len(candles['classification']))

    patterns = []
    for i in range(len(candles['classification'])):
        value = {'value': 0, 'patterns': []}
        for pattern in PATTERNS:
            val = pattern_library(pattern, candles['classification'], i)
            if val[0] != 0:
                value['value'] += val[0]
                modified_pattern = f"{pattern}: {val[1]}"
                value['patterns'].append(modified_pattern)

            vol = pattern_library(pattern, candles['classification'], i, body='vol_body')
            if vol[0] != 0:
                value['value'] += vol[0]
                modified_pattern = f"{pattern}: {vol[1]}"
                value['patterns'].append(modified_pattern)

        if pbar is not None:
            pbar.uptick(increment=divisor)

        patterns.append(value)

    patterns2 = filtered_reversal_patterns(fund, candles)
    tabular = [0.0] * len(patterns)

    for i, pattern in enumerate(patterns2):
        if pattern['value'] != 0:
            patterns[i]['value'] += pattern['value']
            patterns[i]['patterns'].extend(pattern['patterns'])

    for i, pattern in enumerate(patterns):
        tabular[i] += float(pattern['value'])

    if plot_output:
        signal = simple_moving_avg(fund, 10)

        for i, pattern in enumerate(patterns):
            if pattern['value'] != 0:
                signal[i] += (pattern['value'] * 10.0)
                print(f"index {i}: {pattern['value']} => {pattern['patterns']}")

        plot_obj = {"plot": signal, "color": 'black',
                    "legend": 'candlestick signal'}
        generate_plot(
            PlotType.CANDLESTICKS,
            fund,
            **{
                "additional_plots": [plot_obj],
                "title": "Candlestick Signals",
                "plot_output": plot_output
            }
        )

    candles['patterns'] = patterns
    candles['tabular'] = tabular

    return candles


def determine_threshold(fund: pd.DataFrame, **kwargs) -> dict:
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
    long_percentile = kwargs.get('long_percentile', 75)
    short_percentile = kwargs.get('short_percentile', 25)
    doji_percentile = kwargs.get('doji_percentile', 1)
    doji_ratio = kwargs.get('doji_ratio', 8)
    plot_output = kwargs.get('plot_output', True)

    open_close = []
    high_low = []
    for i, op in enumerate(fund['Open']):
        open_close.append(np.abs(op - fund['Close'][i]))
        high_low.append(np.abs(fund['High'][i] - fund['Low'][i]))

    volatility = exponential_moving_avg(high_low, 25, data_type='list')
    long_price = []
    short_price = []
    long_thresh = float(long_percentile) / 100.0
    short_thresh = float(short_percentile) * 2.0 / 100.0
    for i, low in enumerate(fund['Low']):
        price_l = low + (volatility[i] * long_thresh)
        price_s = low + (volatility[i] * short_thresh)
        long_price.append(price_l)
        short_price.append(price_s)

    thresholds = {}
    thresholds['short'] = np.percentile(open_close, short_percentile)
    thresholds['long'] = np.percentile(open_close, long_percentile)
    thresholds['doji'] = np.percentile(open_close, doji_percentile)
    thresholds['doji_ratio'] = doji_ratio
    thresholds['volatility'] = {"long": long_price, "short": short_price}

    if plot_output:
        print(f"\r\nThresholding for candlesticks:")
        print(f"\r\nShort: {thresholds['short']}")
        print(f"Long: {thresholds['long']}")
        print(f"Doji: {thresholds['doji']}")
        print(f"Doji Ratio: {thresholds['doji_ratio']}")
        generate_plot(
            PlotType.CANDLESTICKS,
            fund,
            **{
                "title": "Doji & Long/Short Days",
                "threshold_candles": thresholds,
                "plot_output": plot_output
            }
        )

    return thresholds


def day_classification(fund: pd.DataFrame, thresholds: dict) -> List[dict]:
    """Day Classification

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        thresholds {dict} -- candlestick body sizes

    Returns:
        list[dict] -- each trading period classified by candlesticks
    """
    trading_candles = []
    sma = simple_moving_avg(fund, 10)

    LONG = thresholds['long']
    SHORT = thresholds['short']
    DOJI = thresholds['doji']
    RATIO = thresholds['doji_ratio']

    vol_long = thresholds['volatility']['long']
    vol_short = thresholds['volatility']['short']

    # Classification elements:
    for i, close in enumerate(fund['Close']):
        stats = {}

        # Raw, basic values to start
        stats['basic'] = {}
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
        stats['candlestick'] = {}

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

        trading_candles.append(stats)
    return trading_candles


def get_pattern_signals(candles: dict, position: pd.DataFrame) -> List[dict]:
    """Get Pattern Signals

    Specifically for lastest signals present

    Arguments:
        candle {dict} -- candle data object
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of feature objects
    """
    features = []
    for i, pattern in enumerate(candles['patterns']):
        date = position.index[i].strftime("%Y-%m-%d")

        if pattern['value'] < 0:
            for style in pattern['patterns']:
                data = {
                    "type": 'bearish',
                    "value": style,
                    "index": i,
                    "date": date
                }
                features.append(data)

        elif pattern['value'] > 0:
            for style in pattern['patterns']:
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
    zones = [0.0, 0.0]
    if filter_function == 'stochastic':
        stoch_signals = generate_full_stoch_signal(fund, plot_output=False)
        filter_signal = stoch_signals['smooth_k']
        zones = [80.0, 20.0]
    else:
        return []

    patterns = []
    for i in range(len(candle['classification'])):
        value = {'value': 0, 'patterns': []}
        for pattern_name in ("dark cloud piercing line", "evening morning star"):
            for body in ("body", "vol_body"):
                val = pattern_library(pattern_name, candle['classification'], i, body)
                if val[0] != 0:
                    value['value'] += val[0]
                    modified_pattern = f"{pattern_name}: {val[1]}"
                    value['patterns'].append(modified_pattern)

        patterns.append(value)

    for i in range(1, len(patterns)):
        if patterns[i]['value'] != 0:
            if (filter_signal[i] >= zones[0]) and (filter_signal[i] <= zones[1]):
                patterns[i]['value'] *= 2
            elif (filter_signal[i-1] >= zones[0]) and (filter_signal[i-1] <= zones[1]):
                patterns[i]['value'] *= 2
            else:
                patterns[i] = {'value': 0, 'patterns': []}

    return patterns


###################################
#   PATTERN DETECTION LIBRARY
###################################

def pattern_library(pattern: str,
                    trading_candles: List[dict],
                    index: int,
                    body: str = 'body') -> Tuple[int, str]:
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
    days_needed = PATTERNS[pattern]['days']
    function = PATTERNS[pattern]['function']
    weight = PATTERNS[pattern].get('weight', 1)

    if index < days_needed - 1:
        return 0, ''

    if days_needed == 1:
        sub_days = trading_candles[index].copy()
    else:
        start = (index + 1) - days_needed
        sub_days = trading_candles[start:index+1].copy()

    if isinstance(sub_days, dict):
        sub_days = [sub_days]

    detection = function(sub_days, body)
    if detection:
        if detection['type'] == 'bearish':
            return -1 * weight, detection['style']
        if detection['type'] == 'bullish':
            return 1 * weight, detection['style']

    return 0, ''


###################################


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


PATTERNS = {
    "doji": {'days': 1, 'function': doji_pattern.doji_pattern},
    "dark cloud piercing line": {
        'days': 2,
        'function': dark_cloud_or_piercing_line.dark_cloud_or_piercing_line
    },
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
    "three river": {'days': 3, 'function': three_river.unique_three_river},
    "three stars": {'days': 3, 'function': three_stars.three_stars_in_the_south},
    "concealing baby": {'days': 4, 'function': concealing_baby.concealing_baby_swallow},
    "stick sandwich": {'days': 3, 'function': stick_sandwich.stick_sandwich},
    "identical crows": {'days': 3, 'function': identical_crows.identical_three_crows},
    "deliberation": {'days': 3, 'function': deliberation.deliberation},
    "matching": {'days': 2, 'function': matching.matching_high_low},
    "two crows": {'days': 3, 'function': two_crows.upside_gap_two_crows},
    "homing pigeon": {'days': 2, 'function': homing_pigeon.homing_pigeon},
    "ladder": {'days': 5, 'function': ladder.ladder},
    "advance block": {'days': 3, 'function': advanced_block.advance_block},
    "separating lines": {'days': 2, 'function': separating_lines.separating_lines},
    "tasuki gap": {'days': 3, 'function': tasuki_gap.tasuki_gap_upside_downside},
    "side by side": {'days': 3, 'function': side_by_side.side_by_side_white_lines},
    "three line strike": {'days': 4, 'function': three_line_strike.three_line_strike},
    "gap three methods": {
        'days': 3,
        'function': three_methods.upside_downside_gap_three_methods
    },
    "neck line": {'days': 2, 'function': neckline.on_in_neck_line}
}
