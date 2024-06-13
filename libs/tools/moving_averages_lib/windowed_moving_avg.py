from typing import Union

import pandas as pd
import numpy as np


def windowed_moving_avg(dataset: Union[list, pd.DataFrame],
                        interval: int,
                        data_type: str = 'DataFrame',
                        key: str = 'Close',
                        filter_type: str = 'simple',
                        weight_strength: float = 2.0) -> list:
    """Windowed Moving Average

    Arguments:
        dataset -- tabular data, either list or pd.DataFrame
        interval {int} -- window to windowed moving average

    Optional Args:
        data_type {str} -- either 'DataFrame' or 'list' (default: {'DataFrame'})
        key {str} -- column key (if type 'DataFrame'); (default: {'Close'})
        filter_type {str} -- either 'simple' or 'exponential' (default: {'simple'})
        weight_strength {float} -- numerator for ema weight (default: {2.0})

    Returns:
        list -- filtered data
    """
    # pylint: disable=too-many-arguments,too-many-branches
    if data_type == 'DataFrame':
        data = list(dataset[key])
    else:
        data = dataset

    wma = []
    if interval < len(data) - 3:
        if filter_type == 'simple':
            left = int(np.floor(float(interval) / 2))
            if left == 0:
                return data
            for i in range(left):
                wma.append(data[i])
            for i in range(left, len(data)-left):
                wma.append(np.mean(data[i-(left):i+(left)]))
            for i in range(len(data)-left, len(data)):
                wma.append(data[i])

        elif filter_type == 'exponential':
            left = int(np.floor(float(interval) / 2))
            weight = min(weight_strength / (float(interval) + 1.0), 1.0)
            for i in range(left):
                wma.append(data[i])
            for i in range(left, len(data)-left):
                sum_len = len(data[i-(left):i+(left)]) - 1
                sum_vals = np.sum(data[i-(left):i+(left)])
                sum_vals -= data[i]
                sum_vals = sum_vals / float(sum_len)
                sum_vals = data[i] * weight + sum_vals * (1.0 - weight)
                wma.append(sum_vals)
            for i in range(len(data)-left, len(data)):
                wma.append(data[i])

    return wma