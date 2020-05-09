import os
import pandas as pd
import numpy as np

from libs.utils import dual_plotting, SP500
from .moving_average import typical_price_signal, simple_moving_avg


def commodity_channel_index(position: pd.DataFrame, **kwargs) -> dict:

    cci = dict()

    cci['tabular'] = generate_commodity_signal(position, **kwargs)

    return cci


def generate_commodity_signal(position: pd.DataFrame, **kwargs) -> list:
    """Generate Commodity Signal

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        interval {int} -- period for simple moving average (default: {20})

    Returns:
        list -- tabular commodity channel index signal
    """
    interval = kwargs.get('interval', 20)
    CONSTANT = kwargs.get('constant', .015)
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')

    tabular = []

    tps = typical_price_signal(position)
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
        tabular.append(cci)
        print(f"cci {cci}, mean {mean_dev[i]}, tps {tps[i]}, sma {sma[i]}")

    overbought = [100.0 for _ in range(len(tps))]
    oversold = [-100.0 for _ in range(len(tps))]

    name2 = SP500.get(name, name)
    if plot_output:
        dual_plotting(position['Close'], [tabular, overbought, oversold],
                      'Price', 'CCI', title=f'{name2} - Commodity Channel Index')

    else:
        filename = os.path.join(name, view, f"commodity_channel_{name}.png")
        dual_plotting(position['Close'], [tabular, overbought, oversold],
                      'Price', 'CCI', title=f'{name2} - Commodity Channel Index',
                      saveFig=True, filename=filename)

    return tabular
