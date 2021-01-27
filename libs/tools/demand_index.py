import os
import pandas as pd
import numpy as np

from libs.utils import INDEXES, ProgressBar
from libs.utils import dual_plotting, generic_plotting
from libs.features import normalize_signals
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
    dmx['signals'] = demand_index_indicators(fund, dmx, pbar=pbar)
    dmx['metrics'] = demand_index_metrics(fund, dmx, plot_output=plot_output, name=name, view=view, pbar=pbar)

    if pbar is not None:
        pbar.uptick(increment=0.1)

    return dmx


def demand_index_indicators(fund: pd.DataFrame, dmx: dict, **kwargs) -> list:
    """Demand Index Indicators

    Specifically, look at zero-crossings and divergences (sort of implemented)

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        dmx {dict} -- demand index data object

    Returns:
        list -- demand index data object
    """
    pbar = kwargs.get('pbar')

    signals = di_crossovers(fund, dmx['tabular'])
    if pbar is not None:
        pbar.uptick(increment=0.1)

    signals.extend(di_divergences(fund, dmx['tabular']))
    if pbar is not None:
        pbar.uptick(increment=0.1)

    return signals


def demand_index_metrics(fund: pd.DataFrame, dmx: dict, **kwargs) -> list:
    """Demand Index Metrics

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        dmx {dict} -- demand index data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- demand index data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('pbar')

    metrics = [0.0] * len(dmx['tabular'])

    weight_map = {
        "zero crossover": [1.2, 0.95, 0.6, 0.1],
        "dual-signal-line": [1.0, 0.85, 0.55, 0.1],
        "signal-line zone": [0.8, 0.65, 0.4, 0.1]
    }

    for sig in dmx['signals']:
        ind = sig['index']
        s = 1.0
        if sig['type'] == 'bearish':
            s = -1.0

        if 'dual-signal-line' in sig['value']:
            weights = weight_map['dual-signal-line']
        elif 'signal-line zone' in sig['value']:
            weights = weight_map['signal-line zone']
        else:
            weights = weight_map['zero crossover']
        
        metrics[ind] = s

        # Smooth the curves
        if ind - 1 >= 0:
            metrics[ind-1] += s * weights[1]
        if ind + 1 < len(metrics):
            metrics[ind+1] += s * weights[1]
        if ind - 2 >= 0:
            metrics[ind-2] += s * weights[2]
        if ind + 2 < len(metrics):
            metrics[ind+2] += s * weights[2]
        if ind - 3 >= 0:
            metrics[ind-3] += s * weights[3]
        if ind + 3 < len(metrics):
            metrics[ind+3] += s * weights[3]

    if pbar is not None:
        pbar.uptick(increment=0.1)

    metrics = exponential_moving_avg(metrics, 7, data_type='list')
    norm = normalize_signals([metrics])
    metrics = norm[0]

    if pbar is not None:
        pbar.uptick(increment=0.1)

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Demand Index"
    if plot_output:
        dual_plotting(fund['Close'], metrics, 'Price', 'Demand Index Metrics')
    else:
        filename = os.path.join(name, view, f"demand_index_metrics_{name}")
        dual_plotting(fund['Close'], metrics, 'Price', 'Demand Index Metrics',
                      title=title, saveFig=True, filename=filename)

    return metrics


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
        pbar.uptick(increment=0.05)

    vol_av = simple_moving_avg(vol_hl, 10, data_type='list')
    if pbar is not None:
        pbar.uptick(increment=0.05)

    # Calculate the constant 'K'.
    const_K = [0.0] * len(vol_av)
    for i, vol in enumerate(vol_av):
        if vol == 0.0:
            const_K[i] = 0.0
        else:
            const_K[i] = 3.0 * fund['Close'][i] / vol

    if pbar is not None:
        pbar.uptick(increment=0.05)

    # Calculate daily percent change of open-close.
    percent = [0.0] * len(vol_av)
    for i, ope in enumerate(fund['Open']):
        percent[i] = (fund['Close'][i] - ope) / ope * const_K[i]

    if pbar is not None:
        pbar.uptick(increment=0.05)

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
        pbar.uptick(increment=0.05)

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
        pbar.uptick(increment=0.05)

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


def di_crossovers(fund: pd.DataFrame, signal: list) -> list:
    """Demand Index Crossovers

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        signal {list} -- demand index signal

    Returns:
        list -- list of zero-crossover features
    """
    crossovers = []
    state = 'n'
    data = None
    for i, sig in enumerate(signal):
        date = fund.index[i].strftime("%Y-%m-%d")
        data = None

        if state == 'n':
            if sig > 0.0:
                state = 'u'
            else:
                state = 'e'

        elif state == 'u':
            if sig < 0.0:
                state = 'e'
                data = {
                    "type": 'bearish',
                    "value": 'zero crossover',
                    "index": i,
                    "date": date
                }

        elif state == 'e':
            if sig > 0.0:
                state = 'u'
                data = {
                    "type": 'bullish',
                    "value": 'zero crossover',
                    "index": i,
                    "date": date
                }

        if data is not None:
            crossovers.append(data)

    return crossovers


def di_divergences(fund: pd.DataFrame, signal: list) -> list:
    """Demand Index Divergences

    Note: this is not a typical [or preferred] method of deriving divergences

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        signal {list} -- demand index signal

    Returns:
        list -- list of divergent features
    """
    divs = []
    price = [0.0, 0.0]
    windows = [3, 4, 5, 7, 10]

    for window in windows:
        signal_ma = simple_moving_avg(signal, window, data_type='list')
        meter = [0.0] * len(signal)

        state = 'n'
        for i, sig in enumerate(signal):

            if state == 'n':
                if sig > signal_ma[i]:
                    state = 'u'
                else:
                    state = 'e'

            elif state == 'u':
                if sig < signal_ma[i]:
                    state = 'e'
                    meter[i] = -1.0
                
            elif state == 'e':
                if sig > signal_ma[i]:
                    state = 'u'
                    meter[i] = 1.0

        fund_ma = simple_moving_avg(fund, window)
        funder = [0.0] * len(signal)

        state = 'n'
        for i, fun in enumerate(fund['Close']):
            if state == 'n':
                if fun > fund_ma[i]:
                    state = 'u'
                else:
                    state = 'e'

            elif state == 'u':
                if fun < fund_ma[i]:
                    state = 'e'
                    funder[i] = -1.0
                
            elif state == 'e':
                if fun > fund_ma[i]:
                    state = 'u'
                    funder[i] = 1.0

        
        for i, met in enumerate(meter):
            data = None
            date = fund.index[i].strftime("%Y-%m-%d")

            if met > 0.0:
                if funder[i] < 0.0:
                    data = {
                        "type": 'bullish',
                        "value": f'dual-signal-line {window}d divergence',
                        "index": i,
                        "date": date
                    }

            if met < 0.0:
                if funder[i] > 0.0:
                    data = {
                        "type": 'bearish',
                        "value": f'dual-signal-line {window}d divergence',
                        "index": i,
                        "date": date
                    }

            if data is not None:
                divs.append(data)

    windows = [5, 10]
    for window in windows:
        signal_ma = simple_moving_avg(signal, window, data_type='list')
        fund_ma = simple_moving_avg(fund, window)

        state = 'n'
        for i, sig in enumerate(signal):
            data = None
            date = fund.index[i].strftime("%Y-%m-%d")

            if state == 'n':
                price[0] = fund['Close'][i] - fund_ma[i]
                if sig > signal_ma[i]:
                    state = 'u1'
                else:
                    state = 'e1'

            elif state == 'u1':
                if sig < signal_ma[i]:
                    state = 'e1'
                    price[1] = fund['Close'][i] - fund_ma[i]
                    if price[0] < 0.0 and price[1] < 0.0:
                        data = {
                            "type": 'bullish',
                            "value": f'signal-line zone {window}d divergence',
                            "index": i,
                            "date": date
                        }
                    price[0] = price[1]
                
            elif state == 'e1':
                if sig > signal_ma[i]:
                    state = 'u1'
                    price[1] = fund['Close'][i] - fund_ma[i]
                    if price[0] > 0.0 and price[1] > 0.0:
                        data = {
                            "type": 'bearish',
                            "value": f'signal-line zone {window}d divergence',
                            "index": i,
                            "date": date
                        }
                    price[0] = price[1]

            if data is not None:
                divs.append(data)

    return divs
