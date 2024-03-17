""" Average Directional Index """
import os
from typing import Union

import pandas as pd

from libs.utils import INDEXES, PlotType, generate_plot
from libs.features import normalize_signals

from .trends import auto_trend
from .moving_average import exponential_moving_avg
from .average_true_range import average_true_range


def average_directional_index(fund: pd.DataFrame, atr: Union[list, None] = None, **kwargs) -> dict:
    """Average Directional Index (ADX)

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        atr {list} -- average true range (ATR) signal (default: {[]})

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        dict -- adx data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('progress_bar')

    adx = {}
    if not atr or len(atr) == 0:
        atr = average_true_range(fund, out_suppress=True).get('tabular')

    adx['tabular'] = get_adx_signal(fund, atr, plot_output=plot_output, name=name, view=view)
    adx = adx_metrics(fund, adx, plot_output=plot_output, name=name, view=view)

    adx['length_of_data'] = len(adx['tabular']['adx'])
    adx['type'] = 'oscillator'

    if pbar is not None:
        pbar.uptick(increment=0.1)

    return adx


def get_adx_signal(fund: pd.DataFrame, atr: list, **kwargs) -> dict:
    """Get ADX Signal

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        atr {list} -- atr signal

    Optional Args:
        interval {int} -- lookback period (default: {14})
        adx_default {float} -- default adx signal value before calculations appear
                                (default: {20.0})
        no_trend_value {float} -- threshold of ADX where signal is deemed to not have a trend
                                    (default: {20.0})
        strong_trend_value {float} -- threshold of ADX where signal is deemed to have a strong trend
                                        (default: {25.0})
        high_trend_value {float} -- threshold of ADX where signal drops below as trend weakens
                                        (default: {40.0})
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        pbar {ProgressBar} -- (default: {None})

    Returns:
        dict -- tabular adx and DI signals
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    interval = kwargs.get('interval', 14)
    adx_default = kwargs.get('adx_default', 20.0)
    no_trend = kwargs.get('no_trend_value', 20.0)
    strong_trend = kwargs.get('strong_trend_value', 25.0)
    high_trend = kwargs.get('high_trend_value', 40.0)

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('pbar')

    signal = {}
    # Calculate the directional movement signals
    dmp = [0.0] * len(fund['Close'])
    dmn = [0.0] * len(fund['Close'])
    for i in range(1, len(fund['Close'])):
        dmp[i] = fund['High'][i] - fund['High'][i-1]
        dmn[i] = fund['Low'][i-1] - fund['Low'][i]

        if dmp[i] > dmn[i]:
            dmn[i] = 0.0
        else:
            dmp[i] = 0.0
        if dmp[i] < 0.0:
            dmp[i] = 0.0
        if dmn[i] < 0.0:
            dmn[i] = 0.0

    if pbar is not None:
        pbar.uptick(increment=0.1)

    # Calculate the dm signals, di signals, dx signal with 'interval' averages
    dma_p = [0.0] * len(fund['Close'])
    dma_n = [0.0] * len(fund['Close'])
    di_p = [0.0] * len(fund['Close'])
    di_n = [0.0] * len(fund['Close'])
    dx_signal = [0.0] * len(fund['Close'])

    dma_p[interval-1] = sum(dmp[0:interval])
    dma_n[interval-1] = sum(dmn[0:interval])
    for i in range(interval, len(fund['Close'])):
        dma_p[i] = dma_p[i-1] - (dma_p[i-1] / float(interval)) + dmp[i]
        dma_n[i] = dma_n[i-1] - (dma_n[i-1] / float(interval)) + dmn[i]

        di_p[i] = dma_p[i] / atr[i] * 100.0
        di_n[i] = dma_n[i] / atr[i] * 100.0

        dx_signal[i] = abs(di_p[i] - di_n[i]) / (di_p[i] + di_n[i]) * 100.0

    if pbar is not None:
        pbar.uptick(increment=0.3)

    # Finally, calculate the adx signal as an 'interval' average of dx
    adx_signal = [adx_default] * len(fund['Close'])
    adx_signal[interval-1] = sum(dx_signal[0:interval]) / float(interval)
    for i in range(interval, len(adx_signal)):
        adx_signal[i] = ((adx_signal[i-1] * 13) +
                         dx_signal[i]) / float(interval)

    if pbar is not None:
        pbar.uptick(increment=0.1)

    signal['di_+'] = di_p
    signal['di_-'] = di_n
    signal['adx'] = adx_signal
    signal['high_trend'] = [high_trend] * len(adx_signal)
    signal['no_trend'] = [no_trend] * len(adx_signal)
    signal['strong_trend'] = [strong_trend] * len(adx_signal)

    plots = [
        signal['no_trend'],
        signal['high_trend'],
        signal['strong_trend'],
        signal['adx']
    ]

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Average Directional Index (ADX)"

    generate_plot(
        PlotType.DUAL_PLOTTING,
        fund['Close'],
        **{
            "y_list_2": plots,
            "y1_label": 'Price',
            "y2_label": ['No Trend', 'Over Trend', 'Strong Trend', 'ADX'],
            "title": title,
            "plot_output": plot_output,
            "filename": os.path.join(name, view, f"adx_tabular_{name}.png")
        }
    )

    if pbar is not None:
        pbar.uptick(increment=0.1)

    return signal


def adx_metrics(fund: pd.DataFrame, adx: dict, **kwargs) -> dict:
    """ADX Metricx

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        adx {dict} -- adx data object

    Optional Args:
        plot_output {bool} -- (default: {True})
        name {str} -- (default: {''})
        view {str} -- (default: {''})
        pbar {ProgressBar} -- (default: {None})

    Returns:
        dict -- adx data object
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements,chained-comparison
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('pbar')

    adx['metrics'] = [0.0] * len(fund['Close'])
    adx['signals'] = []

    auto = auto_trend(fund['Close'], periods=[14])

    no_trend = adx['tabular']['no_trend'][0]
    strong_trend = adx['tabular']['strong_trend'][0]
    over_trend = adx['tabular']['high_trend'][0]

    signal = adx['tabular']['adx']
    for i in range(1, len(signal)):
        data = None
        date = fund.index[i].strftime("%Y-%m-%d")

        trend = 0.0
        state = 'none'
        if auto[i] > 0.0:
            trend = 1.0
            state = 'bull'
        elif auto[i] < 0.0:
            trend = -1.0
            state = 'bear'

        if signal[i-1] < no_trend and signal[i] > no_trend:
            adx['metrics'][i] += 1.0 * trend
            if state != 'none':
                data = {
                    "type": state,
                    "value": '20-crossover: trend start',
                    "index": i,
                    "date": date
                }

        if signal[i-1] < strong_trend and signal[i] > strong_trend:
            adx['metrics'][i] += 0.6 * trend
            if state != 'none':
                data = {
                    "type": state,
                    "value": '25-crossover: STRONG trend',
                    "index": i,
                    "date": date
                }

        if signal[i] > strong_trend:
            adx['metrics'][i] += 0.2 * trend

        if signal[i-1] > over_trend and signal[i] < over_trend:
            adx['metrics'][i] += -1.0 * trend
            if state != 'none':
                if state == 'bull':
                    state = 'bear'
                else:
                    state = 'bull'
                data = {
                    "type": state,
                    "value": '40-crossunder: weakening trend',
                    "index": i,
                    "date": date
                }

        if signal[i-1] > no_trend and signal[i] < no_trend:
            adx['metrics'][i] += 0.0
            if state != 'none':
                if state == 'bull':
                    state = 'bear'
                else:
                    state = 'bull'
                data = {
                    "type": state,
                    "value": '20-crossunder: WEAK/NO trend',
                    "index": i,
                    "date": date
                }

        if data is not None:
            adx['signals'].append(data)

    if pbar is not None:
        pbar.uptick(increment=0.1)

    metrics = exponential_moving_avg(adx['metrics'], 7, data_type='list')
    if pbar is not None:
        pbar.uptick(increment=0.1)

    adx['metrics'] = normalize_signals([metrics])[0]

    name2 = INDEXES.get(name, name)
    title = f"{name2} - ADX Metrics"

    generate_plot(
        PlotType.DUAL_PLOTTING,
        fund['Close'],
        **{
            "y_list_2": adx['metrics'],
            "y1_label": 'Price',
            "y2_label": 'Metrics',
            "title": title,
            "plot_output": plot_output,
            "filename": os.path.join(name, view, f"adx_metrics_{name}.png")
        }
    )

    if pbar is not None:
        pbar.uptick(increment=0.2)

    return adx
