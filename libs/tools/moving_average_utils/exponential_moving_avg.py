from typing import Union

import pandas as pd
import numpy as np


def exponential_moving_avg(dataset: Union[list, pd.DataFrame],
                           interval: int,
                           data_type: str = 'DataFrame',
                           key: str = 'Close',
                           ema_factor: float = 2.0) -> list:
    """Exponential Moving Average

    Arguments:
        dataset -- tabular data, either list or pd.DataFrame
        interval {int} -- window to exponential moving average

    Optional Args:
        data_type {str} -- either 'DataFrame' or 'list' (default: {'DataFrame'})
        key {str} -- column key (if type 'DataFrame'); (default: {'Close'})
        ema_factor {float} -- exponential smoothing factor; (default: {2.0})

    Returns:
        list -- filtered data
    """
    if data_type == 'DataFrame':
        data = list(dataset[key])
    else:
        data = dataset

    ema = []
    if interval < len(data) - 3:
        k = ema_factor / (float(interval) + 1.0)
        for i in range(interval-1):
            ema.append(data[i])
        for i in range(interval-1, len(data)):
            ema.append(np.mean(data[i-(interval-1):i+1]))
            if i != interval-1:
                ema[i] = ema[i-1] * (1.0 - k) + data[i] * k
    return ema
