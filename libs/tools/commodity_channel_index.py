import os
import pandas as pd
import numpy as np

from libs.utils import dual_plotting, SP500, ProgressBar
from .moving_average import typical_price_signal, simple_moving_avg


def commodity_channel_index(position: pd.DataFrame, **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    p_bar = kwargs.get('progress_bar')

    cci = dict()

    periods = [20, 40, 80]
    cci['tabular'] = {}
    cci['tabular'] = generate_commodity_signal(
        position, intervals=periods, plot_output=plot_output, name=name, view=view)

    cci = cci_feature_detection(position, cci)

    if p_bar is not None:
        p_bar.uptick(increment=1.0)

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
    intervals = kwargs.get('intervals', [10, 20, 40])
    CONSTANT = kwargs.get('constant', .015)
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

        for i in range(len(tps)):
            cci = (tps[i] - sma[i]) / (CONSTANT * mean_dev[i])
            tabular[str(interval)].append(cci)

    overbought = [100.0 for _ in range(len(tps))]
    oversold = [-100.0 for _ in range(len(tps))]

    plots = [tabular[tab] for tab in tabular]
    plots.append(overbought)
    plots.append(oversold)

    name2 = SP500.get(name, name)
    period_strs = ', '.join(intervals)
    title = f'{name2} - Commodity Channel Index ({period_strs} periods)'
    if plot_output:
        dual_plotting(position['Close'], plots,
                      'Price', 'CCI', title=title)

    else:
        filename = os.path.join(name, view, f"commodity_channel_{name}.png")
        dual_plotting(position['Close'], plots,
                      'Price', 'CCI', title=title,
                      saveFig=True, filename=filename)

    return tabular


def cci_feature_detection(position: pd.DataFrame, cci: dict) -> dict:

    cci['features'] = []

    for period in cci['tabular']:
        cci['features'].extend(get_crossover_features(
            position, cci['tabular'][period], period))

    return cci


def get_crossover_features(position: pd.DataFrame, signal: list, period: str) -> list:

    features = []
    state = 'x'
    for i, comp in enumerate(signal):
        date = position.index[i]

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

        elif state == 'n2':
            if comp > 0.0:
                state = 'p1'

    return features
