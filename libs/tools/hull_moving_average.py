import pandas as pd
import numpy as np

from libs.utils import ProgressBar, dual_plotting
from .moving_average import weighted_moving_avg


def hull_moving_average(position: pd.DataFrame, **kwargs) -> dict:
    """Hull Moving Average

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- hull ma data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    p_bar = kwargs.get('progress_bar')

    hull = dict()
    hull['tabular'] = generate_hull_signal(position, plot_output=plot_output)

    return hull


def generate_hull_signal(position: pd.DataFrame, **kwargs) -> list:

    period = kwargs.get('period', 16)
    plot_output = kwargs.get('plot_output', True)
    signal = []

    n_div_2 = weighted_moving_avg(position, int(period/2))
    n = weighted_moving_avg(position, period)

    wma = []
    for i, d in enumerate(n_div_2):
        t = 2.0 * d - n[i]
        wma.append(t)

    sq_period = int(np.round(np.sqrt(float(period)), 0))
    hma = weighted_moving_avg(wma, sq_period, data_type='list')

    if plot_output:
        dual_plotting(position['Close'], hma, 'Price', 'Hull Moving Average')

    return signal
