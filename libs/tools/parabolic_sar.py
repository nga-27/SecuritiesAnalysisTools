import os
import pprint
import pandas as pd
import numpy as np

from libs.utils import candlestick_plot, INDEXES

from .trends import autotrend


def parabolic_sar(fund: pd.DataFrame, adx_tabular: dict = None, **kwargs) -> dict:
    """Parabolic Stop and Reverse (SAR)

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        adx_tabular {dict} -- ADX signal for trend filtering, currently unimplemented
                                (default: {None})

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- SAR data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    p_bar = kwargs.get('progress_bar')

    sar = dict()
    sar = generate_sar(
        fund, plot_output=plot_output, name=name, view=view, p_bar=p_bar)

    sar = sar_metrics(fund, sar)

    if p_bar is not None:
        p_bar.uptick(increment=0.3)

    sar['type'] = 'trend'
    sar['length_of_data'] = len(sar['tabular']['fast'])
    sar['current'] = {
        "fast type": '',
        "slow type": '',
        "fast price": 0.0,
        "slow price": 0.0,
        "current price": 0.0
    }

    sar['current']['fast_price'] = sar['tabular']['fast'][-1]
    sar['current']['slow_price'] = sar['tabular']['slow'][-1]
    sar['current']['curr_price'] = fund['Close'][-1]

    sar['current']['fast_type'] = 'Stop Loss'
    sar['current']['slow_type'] = 'Stop Loss'
    if sar['current']['fast_price'] > sar['current']['curr_price']:
        sar['current']['fast_type'] = 'Entry Point'
    if sar['current']['slow_price'] > sar['current']['curr_price']:
        sar['current']['slow_type'] = 'Entry Point'

    if plot_output:
        print(f"\r\nParabolic SAR Status:\r\n")
        pprint.pprint(sar['current'])

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    return sar


def generate_sar(fund: pd.DataFrame, **kwargs) -> dict:
    """Generate Stop and Reverse (SAR) Signal

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        af {list} -- acceleration factor (default: {[0.02, 0.01]})
        max_factor {float} -- max acceleration factor (default: {0.2})
        period_offset {int} -- lookback period to establish a trend in starting
                                (default: {5})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        p_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- sar data object; signals (different AFs)
    """
    # Note, higher/faster AF should be first of 2
    ACC_FACTOR = kwargs.get('af', [0.02, 0.01])
    MAX_FACTOR = kwargs.get('max_factor', 0.2)
    period_offset = kwargs.get('period_offset', 5)

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    p_bar = kwargs.get('pbar')

    sar_dict = dict()

    signals = {"fast": [], "slow": []}
    sig_names = ["fast", "slow"]
    colors = ["blue", "black"]
    indicators = []

    signal = [0.0] * len(fund['Close'])
    auto = autotrend(fund['Close'], periods=[4])

    # Observe for an 'offset' amount of time before starting
    ep_high = 0.0
    ep_low = float('inf')
    for i in range(period_offset):
        signal[i] = fund['Close'][i]

        if fund['Low'][i] < ep_low:
            ep_low = fund['Low'][i]

        if fund['High'][i] > ep_high:
            ep_high = fund['High'][i]

    # Determine an initial trend to start
    trend = 'down'
    e_p = ep_low
    signal[period_offset-1] = ep_high

    if auto[period_offset-1] > 0.0:
        trend = 'up'
        e_p = ep_high
        signal[period_offset-1] = ep_low

    add_plts = []

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    # Begin generating SAR signal, number of signals determined by number of AFs
    for k, afx in enumerate(ACC_FACTOR):
        a_f = afx

        for i in range(period_offset, len(signal)):
            data = None
            date = fund.index[i].strftime("%Y-%m-%d")

            if trend == 'down':
                sar_i = signal[i-1] - a_f * (signal[i-1] - e_p)
                if fund['High'][i] > sar_i:
                    # Broken downward trend. Stop and reverse!
                    a_f = afx
                    sar_i = e_p
                    e_p = fund['High'][i]
                    trend = 'up'
                    data = {
                        "type": 'bullish',
                        "value": f'downtrend broken-{sig_names[k]}',
                        "index": i,
                        "date": date
                    }

                else:
                    if fund['Low'][i] < e_p:
                        e_p = fund['Low'][i]
                        a_f += afx
                        if a_f > MAX_FACTOR:
                            a_f = MAX_FACTOR

            else:
                sar_i = signal[i-1] + a_f * (e_p - signal[i-1])
                if fund['Low'][i] < sar_i:
                    # Broken upward trend.  Stop and reverse!
                    a_f = afx
                    sar_i = e_p
                    e_p = fund['Low'][i]
                    trend = 'down'
                    data = {
                        "type": 'bearish',
                        "value": f'upward broken-{sig_names[k]}',
                        "index": i,
                        "date": date
                    }

                else:
                    if fund['High'][i] > e_p:
                        e_p = fund['High'][i]
                        a_f += afx
                        if a_f > MAX_FACTOR:
                            a_f = MAX_FACTOR

            signal[i] = sar_i

            if data is not None:
                indicators.append(data)

        signals[sig_names[k]] = signal.copy()
        add_plts.append({
            "plot": signals[sig_names[k]],
            "style": 'scatter',
            "legend": f'Parabolic SAR-{sig_names[k]}',
            "color": colors[k]
        })

        if p_bar is not None:
            p_bar.uptick(increment=0.2)

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Parabolic SAR"

    if plot_output:
        candlestick_plot(fund, additional_plts=add_plts, title=title)
    else:
        filename = os.path.join(name, view, f"parabolic_sar_{name}")
        candlestick_plot(fund, additional_plts=add_plts, title=title,
                         save_fig=True, filename=filename)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    sar_dict['tabular'] = signals
    sar_dict['signals'] = indicators

    return sar_dict


def sar_metrics(fund: pd.DataFrame, sar: dict, **kwargs) -> dict:
    """SAR Metrics

    Primarily percent away from a given SAR trend

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        sar {dict} -- SAR data object

    Returns:
        dict -- SAR data object
    """
    metrics = {"fast_0.02": [], "slow_0.01": []}
    tab = sar['tabular']
    for i, close in enumerate(fund['Close']):
        metrics['fast_0.02'].append(
            np.round((close - tab['fast'][i]) / tab['fast'][i] * 100.0, 3))
        metrics['slow_0.01'].append(
            np.round((close - tab['slow'][i]) / tab['slow'][i] * 100.0, 3))

    sar['metrics'] = metrics

    return sar
