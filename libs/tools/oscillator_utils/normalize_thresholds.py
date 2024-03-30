""" Normalize Thresholds """
from typing import List, Union, Tuple

import pandas as pd

from libs.tools.moving_averages_lib.simple_moving_avg import simple_moving_avg
from .constants import OVERBOUGHT_THRESHOLD, OVERSOLD_THRESHOLD


def normalize_oscillator_threshold_signals(position: pd.DataFrame,
                                           moving_avg_periods: Union[List[int], int, None] = None,
                                           base_low: float=OVERSOLD_THRESHOLD,
                                           base_high: float=OVERBOUGHT_THRESHOLD
                                           ) -> Tuple[List[float], List[float]]:
    """Adjust the low and high thresholds dynamically by factoring in various trend weights.
    Typically, an oscillator will skew during a trend. During a strong uptrend, RSI or other
    oscillator indicators could be 80-90 consistently, constantly triggering overbought signals.
    This function normalizes those thresholds dynamically based on various trend periods.

    Args:
        position (pd.DataFrame): price of the equity
        moving_avg_periods (Union[List[int], int, None], optional): List of ints or int of moving
                                        average periods. When None, default: [20, 50, 100, 200].
                                        Defaults to None.
        base_low (float, optional): Standard, in flat trend low value. Typically 30.
                                    Defaults to OVERSOLD_THRESHOLD.
        base_high (float, optional): Standard, in flat trend high value. Typically 70.
                                    Defaults to OVERBOUGHT_THRESHOLD.

    Returns:
        Tuple[List[float], List[float]]: list of lows, list of highs
    """
    # pylint: disable=too-many-locals
    if moving_avg_periods is None:
        moving_avg_periods = [20, 50, 100, 200]
    if isinstance(moving_avg_periods, int):
        moving_avg_periods = [moving_avg_periods]
    moving_avg_periods.sort()

    lows = [base_low] * len(position['Close'])
    highs = [base_high] * len(position['Close'])

    moving_averages = []
    weights = []
    max_sum = min(base_low, 100.0 - base_high) / 2.0
    summed_weights = sum(moving_avg_periods)
    for period in moving_avg_periods:
        moving_averages.append(simple_moving_avg(position, period))
        weights.append(float(period) / float(summed_weights) * float(max_sum))

    for i, price in enumerate(position['Close']):
        for j, moving_avg in enumerate(moving_averages):
            if price > moving_avg[i]:
                highs[i] += weights[j]
                lows[i] += weights[j]
            if price < moving_avg[i]:
                highs[i] -= weights[j]
                lows[i] -= weights[j]

    smoothed_low = simple_moving_avg(lows, 21, 'list')
    smoothed_high = simple_moving_avg(highs, 21, 'list')
    return smoothed_low, smoothed_high
