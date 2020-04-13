import pprint
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
    candle['patterns'] = pattern_detection(fund, candle)

    if plot_output:
        candlestick(fund, title=name)
    else:
        filename = f"{name}/{view}/candlestick_{name}"
        candlestick(fund, title=name, filename=filename,
                    saveFig=True)
    return candle


def pattern_detection(fund: pd.DataFrame, candle: dict, **kwargs) -> dict:

    patterns = dict()

    return patterns


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
    LONG = kwargs.get('long_percentile', 85)
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
