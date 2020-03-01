import pandas as pd
import numpy as np

from libs.utils import ProgressBar, generic_plotting
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

    hull = generate_hull_signal(
        position, plot_output=plot_output, name=name, p_bar=p_bar)

    if p_bar is not None:
        p_bar.uptick(increment=1.0)

    return hull


def generate_hull_signal(position: pd.DataFrame, **kwargs) -> list:
    """Generate Hull Signal

    Similar to triple moving average, this produces 3 period hull signals

    Arguments:
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        period {list} -- list of ints for 3 lookback periods (default: {9, 16, 36})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- hull data object
    """
    period = kwargs.get('period', [9, 16, 36])
    plot_output = kwargs.get('plot_output', True)

    hull = {'short': period[0], 'medium': period[1],
            'long': period[2], 'tabular': {}}
    plots = []
    for per in period:
        n_div_2 = weighted_moving_avg(position, int(per/2))
        n = weighted_moving_avg(position, per)

        wma = []
        for i, d in enumerate(n_div_2):
            t = (2.0 * d) - n[i]
            wma.append(t)

        sq_period = int(np.round(np.sqrt(float(per)), 0))
        hma = weighted_moving_avg(wma, sq_period, data_type='list')
        plots.append(hma.copy())

    hull['tabular'] = {'short': plots[0], 'medium': plots[1], 'long': plots[2]}

    if plot_output:
        legend = ['Price', 'HMA-short', 'HMA-medium', 'HMA-long']
        generic_plotting([position['Close'], plots[0], plots[1],
                          plots[2]], legend=legend, title='Hull Moving Average')

    return hull
