""" commodity channel index """
import os
import datetime
from typing import Union

import pandas as pd
import numpy as np

from libs.utils import INDEXES, generate_plot, PlotType
from libs.utils.progress_bar import ProgressBar, update_progress_bar
from libs.features.feature_utils import normalize_signals

from .moving_average import typical_price_signal
from .moving_averages_lib.exponential_moving_avg import exponential_moving_avg
from .moving_averages_lib.simple_moving_avg import simple_moving_avg


def commodity_channel_index(position: pd.DataFrame, **kwargs) -> dict:
    """Commodity Channel Index

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {ProgressBar})

    Returns:
        dict -- cci data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    p_bar: Union[ProgressBar, None] = kwargs.get('progress_bar')

    cci = {}
    periods = [20, 40, 80]
    cci['periods'] = {'short': periods[0], 'medium': periods[1], 'long': periods[2]}
    cci['tabular'] = {}
    cci['tabular'] = generate_commodity_signal(
        position, intervals=periods, plot_output=plot_output, name=name, view=view)
    update_progress_bar(p_bar, 0.3)

    cci['signals'] = cci_feature_detection(position, cci)
    update_progress_bar(p_bar, 0.3)

    cci['metrics'] = cci_metrics(
        position, cci, plot_output=plot_output, name=name, view=view)
    update_progress_bar(p_bar, 0.3)

    cci['type'] = 'oscillator'
    cci['length_of_data'] = len(cci['tabular'][str(periods[0])])
    update_progress_bar(p_bar, 0.1)
    return cci


def generate_commodity_signal(position: pd.DataFrame, **kwargs) -> list:
    """Generate Commodity Signal

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        intervals {list} -- period for simple moving average (default: {[20, 40]})

    Returns:
        list -- tabular commodity channel index signal
    """
    # pylint: disable=too-many-locals
    intervals = kwargs.get('intervals', [10, 20, 40])
    constant = kwargs.get('constant', .015)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')

    tabular = {str(per): [] for per in intervals}
    tps = typical_price_signal(position)

    for interval in intervals:
        sma = simple_moving_avg(tps, interval, data_type='list')

        mean_dev = [0.0] * len(tps)
        for i in range(interval, len(tps)):
            sma_val = sma[i]
            sum_devs = 0.0
            for j in range(i-interval, i):
                sum_devs += np.abs(tps[j] - sma_val)

            mean_dev[i] = sum_devs / float(interval)

        for i in range(interval):
            # Avoid dividing by 0
            mean_dev[i] = mean_dev[interval]

        for i, tp_ in enumerate(tps):
            cci = (tp_ - sma[i]) / (constant * mean_dev[i])
            tabular[str(interval)].append(cci)

    overbought = [100.0] * len(tps)
    oversold = [-100.0] * len(tps)

    plots = [tabular[tab] for tab in tabular]
    plots.append(overbought)
    plots.append(oversold)

    name2 = INDEXES.get(name, name)
    period_strs = [str(interval) for interval in intervals]
    period_strs = ', '.join(period_strs)
    title = f'{name2} - Commodity Channel Index ({period_strs} periods)'

    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **{
            "y_list_2": plots, "y1_label": 'Price', "y2_label": 'CCI', "title": title,
            "plot_output": plot_output,
            "filename": os.path.join(name, view, f"commodity_channel_{name}.png")
        }
    )
    return tabular


def cci_feature_detection(position: pd.DataFrame, cci: dict) -> list:
    """CCI Feature Detection

    Arguments:
        position {pd.DataFrame} -- fund dataset
        cci {dict} -- cci data object

    Returns:
        list -- list of features
    """
    features = []
    for period in cci['tabular']:
        features.extend(get_crossover_features(
            position, cci['tabular'][period], period))

    features.sort(key=lambda x: x['index'])
    return features


def cci_metrics(position: pd.DataFrame, cci: dict, **kwargs) -> list:
    """ cci metrics """
    # pylint: disable=too-many-locals,too-many-branches
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')

    metrics = [0.0] * len(position['Close'])
    features = cci['signals']
    signals = cci['tabular']
    periods = cci['periods']

    for feat in features:
        if 'zero' in feat['value']:
            if feat['type'] == 'bullish':
                metrics[feat['index']] += 0.6
            else:
                metrics[feat['index']] -= 0.6

        elif '100' in feat['value']:
            if feat['type'] == 'bullish':
                metrics[feat['index']] += 1.0
            else:
                metrics[feat['index']] -= 1.0

    for period in signals:
        if period == str(periods['short']):
            point = 0.2
        elif period == str(periods['medium']):
            point = 0.2
        else:
            point = 0.2

        for i, value in enumerate(signals[period]):
            if value > 100.0:
                metrics[i] += point
            if value < 100.0:
                metrics[i] -= point

    metrics = exponential_moving_avg(metrics, 7, data_type='list')
    norm = normalize_signals([metrics])
    metrics = norm[0]

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Commodity Channel Index Metrics"

    generate_plot(
        PlotType.DUAL_PLOTTING, position['Close'], **{
            "y_list_2": metrics, "y1_label": 'Price', "y2_label": 'Metrics', "title": title,
            "plot_output": plot_output, "filename": os.path.join(
                name, view, f"commodity_metrics_{name}.png")
        }
    )
    return metrics


def get_crossover_features(position: pd.DataFrame, signal: list, period: str) -> list:
    """Get Crossover Features

    Arguments:
        position {pd.DataFrame} -- fund dataset
        signal {list} -- cci signal
        period {str} -- period of cci signal

    Returns:
        list -- list of crossover features
    """
    # pylint: disable=too-many-branches
    features = []
    state = 'x'
    for i, comp in enumerate(signal):
        date = datetime.datetime.strftime(position.index[i], "%Y-%m-%d")

        if state == 'x':
            if comp > 0.0:
                state = 'p1'
            else:
                state = 'n1'

        elif state == 'n1':
            if comp > 0.0:
                state = 'p1'
            elif comp <= -100.0:
                state = 'n2'
                feat = {
                    "type": 'bearish',
                    "value": f'crossover to -100 ({period})',
                    "index": i,
                    "date": date
                }
                features.append(feat)

        elif state == 'p1':
            if comp < 0.0:
                state = 'n1'

            elif comp >= 100.0:
                state = 'p2'
                feat = {
                    "type": 'bullish',
                    "value": f'crossover to +100 ({period})',
                    "index": i,
                    "date": date
                }
                features.append(feat)

        elif state == 'p2':
            if comp < 0.0:
                state = 'n1'
                feat = {
                    "type": 'bearish',
                    "value": f'zero crossover ({period})',
                    "index": i,
                    "date": date
                }
                features.append(feat)

        elif state == 'n2':
            if comp > 0.0:
                state = 'p1'
                feat = {
                    "type": 'bullish',
                    "value": f'zero crossover ({period})',
                    "index": i,
                    "date": date
                }
                features.append(feat)

    return features
