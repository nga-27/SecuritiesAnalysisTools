import os
import pandas as pd
import numpy as np

from libs.utils import candlestick_plot
from libs.utils import ProgressBar, INDEXES
from .trends import autotrend


def parabolic_sar(fund: pd.DataFrame, adx_tabular: dict = None, **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    p_bar = kwargs.get('progress_bar')

    sar = dict()
    sar['tabular'] = generate_sar(
        fund, plot_output=plot_output, name=name, view=view, p_bar=p_bar)

    if p_bar is not None:
        p_bar.uptick(increment=0.6)

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
        dict -- sar signals (different AFs)
    """
    # Note, higher/faster AF should be first of 2
    ACC_FACTOR = kwargs.get('af', [0.02, 0.01])
    MAX_FACTOR = kwargs.get('max_factor', 0.2)
    period_offset = kwargs.get('period_offset', 5)

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    p_bar = kwargs.get('pbar')

    signals = {"fast": [], "slow": []}
    sig_names = ["fast", "slow"]
    colors = ["blue", "black"]

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

            if trend == 'down':
                sar_i = signal[i-1] - a_f * (signal[i-1] - e_p)
                if fund['High'][i] > sar_i:
                    # Broken downward trend. Stop and reverse!
                    a_f = afx
                    sar_i = e_p
                    e_p = fund['High'][i]
                    trend = 'up'

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

                else:
                    if fund['High'][i] > e_p:
                        e_p = fund['High'][i]
                        a_f += afx
                        if a_f > MAX_FACTOR:
                            a_f = MAX_FACTOR

            signal[i] = sar_i

        signals[sig_names[k]] = signal.copy()
        add_plts.append({
            "plot": signals[sig_names[k]],
            "style": 'scatter',
            "legend": f'Parabolic SAR-{sig_names[k]}',
            "color": colors[k]
        })

        if p_bar is not None:
            p_bar.uptick(increment=0.1)

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Parabolic SAR"

    if plot_output:
        candlestick_plot(fund, additional_plts=add_plts, title=title)
    else:
        filename = os.path.join(name, view, f"parabolic_sar_{name}")
        candlestick_plot(fund, additional_plts=add_plts, title=title,
                         saveFig=True, filename=filename)

    if p_bar is not None:
        p_bar.uptick(increment=0.1)

    return signals
