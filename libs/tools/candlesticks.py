""" candlesticks """
import os
from typing import Tuple, List

import pandas as pd
import numpy as np

from libs.utils import INDEXES, generate_plot, PlotType

from .full_stochastic import generate_full_stoch_signal
from .moving_averages_lib.utils import adjust_signals
from .moving_averages_lib.simple_moving_avg import simple_moving_avg
from .moving_averages_lib.exponential_moving_avg import exponential_moving_avg

from .candlestick_patterns import (
    doji_pattern, dark_cloud_or_piercing_line, inside_outside, neckline, three_methods,
    three_line_strike, side_by_side, tasuki_gap, separating_lines, advanced_block, ladder,
    homing_pigeon, two_crows, matching, deliberation, identical_crows, stick_sandwich,
    concealing_baby, three_stars, three_river, kicking, breakaway, tri_star, three_soldier_crows,
    meeting_line, harami, engulfing, belt_hold, shooting_star, hammers, hanging_man,
    evening_morning_star
)

PATTERNS = {
    "doji": {'days': 1, 'function': doji_pattern.doji_pattern},
    "dark cloud piercing line": {
        'days': 2,
        'function': dark_cloud_or_piercing_line.dark_cloud_or_piercing_line
    },
    "evening morning star": {'days': 3, 'function': evening_morning_star.evening_morning_star},
    "three methods": {'days': 5, 'function': three_methods.rising_falling_three_methods},
    "hammer": {'days': 1, 'function': hammers.hammer_positive},
    "hanging man": {'days': 1, 'function': hanging_man.hanging_man},
    "inverted hammer": {'days': 2, 'function': hammers.inverted_hammer},
    "shooting star": {'days': 2, 'function': shooting_star.shooting_star},
    "belt hold": {'days': 1, 'function': belt_hold.belt_hold},
    "engulfing": {'days': 2, 'function': engulfing.engulfing},
    "harami": {'days': 2, 'function': harami.harami},
    "doji star": {'days': 2, 'function': doji_pattern.doji_star},
    "meeting line": {'days': 2, 'function': meeting_line.meeting_line},
    "three soldier crows": {
        'days': 3,
        'function': three_soldier_crows.three_white_soldiers_black_crows
    },
    "tri star": {'days': 3, 'function': tri_star.tri_star, "weight": 3},
    "breakaway": {'days': 5, 'function': breakaway.breakaway},
    "three inside": {'days': 3, 'function': inside_outside.three_inside},
    "three outside": {'days': 3, 'function': inside_outside.three_outside},
    "kicking": {'days': 2, 'function': kicking.kicking},
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
    # pylint: disable=too-many-locals
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
    # pylint: disable=too-many-locals
    long_percentile = kwargs.get('long_percentile', 75)
    short_percentile = kwargs.get('short_percentile', 25)
    doji_percentile = kwargs.get('doji_percentile', 1)
    doji_ratio = kwargs.get('doji_ratio', 8)
    plot_output = kwargs.get('plot_output', True)

    open_close = []
    high_low = []
    for i, open_val in enumerate(fund['Open']):
        open_close.append(np.abs(open_val - fund['Close'][i]))
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
        print("\r\nThresholding for candlesticks:")
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
    # pylint: disable=too-many-branches
    trading_candles = []
    sma = simple_moving_avg(fund, 10)

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

        if diff >= thresholds['long']:
            stats['candlestick']['body'] = 'long'
        elif diff <= thresholds['short']:
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
        if diff <= thresholds['doji']:
            if stats['candlestick']['shadow_ratio'] >= thresholds['doji_ratio']:
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
