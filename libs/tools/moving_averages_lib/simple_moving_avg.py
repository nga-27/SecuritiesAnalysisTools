from typing import Union

import pandas as pd
import numpy as np


def simple_moving_avg(dataset: Union[list, pd.DataFrame],
                      interval: int,
                      data_type: str = 'DataFrame',
                      key: str = 'Close') -> list:
    """Simple Moving Average

    Arguments:
        dataset -- tabular data, either list or pd.DataFrame
        interval {int} -- window to windowed moving average

    Optional Args:
        data_type {str} -- either 'DataFrame' or 'list' (default: {'DataFrame'})
        key {str} -- column key (if type 'DataFrame'); (default: {'Close'})

    Returns:
        list -- filtered data
    """
    if data_type == 'DataFrame':
        data = list(dataset[key])
    else:
        data = dataset

    moving_average = []
    if interval < len(data) - 3:
        for i in range(interval-1):
            moving_average.append(data[i])
        for i in range(interval-1, len(data)):
            average = np.mean(data[i-(interval-1):i+1])
            moving_average.append(average)
    return moving_average
