import pprint
from copy import deepcopy
import pandas as pd
import numpy as np

from libs.utils import candlestick
from .moving_average import simple_moving_avg


def candlesticks(fund: pd.DataFrame, **kwargs) -> dict:

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
    LONG = kwargs.get('long_percentile', 80)
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
        if diff <= DOJI:
            if diff > 0.0:
                stats['candlestick']['shadow_ratio'] = shadow_length / diff
            if stats['candlestick']['shadow_ratio'] >= RATIO:
                stats['candlestick']['doji'] = True

        days.append(stats)
    return days


###################################
#   PATTERN DETECTION LIBRARY
###################################

def pattern_library(pattern: str, days: list, index: int) -> list:
    days_needed = PATTERNS.get(pattern, {}).get('days', 1)
    function = PATTERNS.get(pattern, {}).get('function')

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
        print(f"PATTERN: {detection} on index {index}")
        if detection['type'] == 'bearish':
            return -1, detection['style']
        if detection['type'] == 'bullish':
            return 1, detection['style']

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


PATTERNS = {
    "doji": {'days': 1, 'function': doji_pattern},
    "dark_cloud_piercing_line": {'days': 2, 'function': dark_cloud_or_piercing_line}
}
