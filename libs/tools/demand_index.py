import os
import pandas as pd
import numpy as np

from libs.utils import INDEXES, ProgressBar
from libs.utils import dual_plotting
from .moving_average import simple_moving_avg, exponential_moving_avg
from .trends import get_trendlines_regression


def demand_index(fund: pd.DataFrame, **kwargs) -> dict:
    """Demand Index

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})
        trendlines {bool} -- if True, will do trendline regression on signal (default: {False})

    Returns:
        dict -- demand index data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('progress_bar')
    trendlines = kwargs.get('trendlines', False)

    dmx = dict()
    dmx['tabular'] = generate_di_signal(
        fund, plot_output=plot_output, name=name, view=view, pbar=pbar)

    if trendlines:
        end = len(dmx['tabular'])
        dmx_trend = dmx['tabular'][end-100: end]
        get_trendlines_regression(
            dmx_trend, plot_output=True, indicator='Demand Index')

    dmx['type'] = 'oscillator'
    dmx['length_of_data'] = len(dmx['tabular'])
    dmx['signals'] = demand_index_indicators(fund, dmx)

    if pbar is not None:
        pbar.uptick(increment=0.1)

    return dmx


def generate_di_signal(fund: pd.DataFrame, **kwargs) -> list:
    """Generate Demand Index Signal

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- demand index signal
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('pbar')

    signal = []

    # First, generate the "2d H-L volatility" signal.
    vol_hl = [0.0] * len(fund['Close'])
    for i in range(1, len(vol_hl)):
        high = max([fund['High'][i], fund['High'][i-1]])
        low = min([fund['Low'][i], fund['Low'][i-1]])
        vol_hl[i] = high - low

    if pbar is not None:
        pbar.uptick(increment=0.1)

    vol_av = simple_moving_avg(vol_hl, 10, data_type='list')
    if pbar is not None:
        pbar.uptick(increment=0.1)

    # Calculate the constant 'K'.
    const_K = [0.0] * len(vol_av)
    for i, vol in enumerate(vol_av):
        if vol == 0.0:
            const_K[i] = 0.0
        else:
            const_K[i] = 3.0 * fund['Close'][i] / vol

    if pbar is not None:
        pbar.uptick(increment=0.1)

    # Calculate daily percent change of open-close.
    percent = [0.0] * len(vol_av)
    for i, ope in enumerate(fund['Open']):
        percent[i] = (fund['Close'][i] - ope) / ope * const_K[i]

    if pbar is not None:
        pbar.uptick(increment=0.1)

    # Calculate BP and SP, so we can get DI = BP/SP | SP/BP
    B_P = []
    S_P = []
    for i, vol in enumerate(fund['Volume']):
        if percent[i] == 0.0:
            B_P.append(0.0)
            S_P.append(0.0)
        elif percent[i] > 0.0:
            B_P.append(vol)
            S_P.append(vol / percent[i])
        else:
            B_P.append(vol / percent[i])
            S_P.append(vol)

    if pbar is not None:
        pbar.uptick(increment=0.2)

    for i, bpx in enumerate(B_P):
        if abs(bpx) > abs(S_P[i]):
            signal.append(S_P[i] / bpx)
        else:
            if abs(bpx) == 0.0 and abs(S_P[i]) == 0.0:
                signal.append(0.0)
            else:
                signal.append(bpx / S_P[i])

    if pbar is not None:
        pbar.uptick(increment=0.1)

    signal = exponential_moving_avg(signal, 10, data_type='list')
    if pbar is not None:
        pbar.uptick(increment=0.1)

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Demand Index"
    if plot_output:
        dual_plotting(fund['Close'], signal, 'Price',
                      'Demand Index', title=title)
    else:
        filename = os.path.join(name, view, f"demand_index_{name}")
        dual_plotting(fund['Close'], signal, 'Price', 'Demand Index',
                      title=title, saveFig=True, filename=filename)

    if pbar is not None:
        pbar.uptick(increment=0.1)

    return signal


def demand_index_indicators(fund: pd.DataFrame, dmx: dict, **kwargs) -> list:
    """Demand Index Indicators

    Specifically, look at zero-crossings and divergences (not implemented yet)

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        dmx {dict} -- demand index data object

    Returns:
        list -- demand index data object
    """

    return dmx
