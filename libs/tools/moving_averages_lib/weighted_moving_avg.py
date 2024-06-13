from typing import Union

import pandas as pd
import numpy as np

def weighted_moving_avg(dataset: Union[list, pd.DataFrame],
                        interval: int,
                        data_type: str = 'DataFrame',
                        key: str = 'Close') -> list:
    """Weighted Moving Average

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

    wma = []
    for i in range(interval):
        wma.append(data[i])

    divisor = 0
    for i in range(interval):
        divisor += i+1

    for i in range(interval, len(data)):
        average = 0.0
        for j in range(interval):
            average += float(j+1) * data[i - (interval-1-j)]
        average = average / float(divisor)
        wma.append(average)
    return wma
