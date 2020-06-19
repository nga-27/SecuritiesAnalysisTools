import os
import pandas as pd
import numpy as np

from libs.utils import ProgressBar, INDEXES
from libs.utils import dual_plotting


def average_directional_index(fund: pd.DataFrame, atr: list = [], **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('progress_bar')

    adx = dict()
    if len(atr) == 0:
        return adx

    adx['tabular'] = get_adx_signal(
        fund, atr, plot_output=plot_output, name=name, view=view)

    if pbar is not None:
        pbar.uptick(increment=1.0)

    return adx


def get_adx_signal(fund: pd.DataFrame, atr: list, **kwargs) -> dict:

    interval = kwargs.get('interval', 14)
    ADX_DEFAULT = kwargs.get('adx_default', 20.0)
    NO_TREND = kwargs.get('no_trend_value', 20.0)
    STRONG_TREND = kwargs.get('strong_trend_value', 25.0)
    HIGH_TREND = kwargs.get('high_trend_value', 40.0)

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')

    signal = dict()

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

    # Finally, calculate the adx signal as an 'interval' average of dx
    adx_signal = [ADX_DEFAULT] * len(fund['Close'])
    adx_signal[interval-1] = sum(dx_signal[0:interval]) / float(interval)
    for i in range(interval, len(adx_signal)):
        adx_signal[i] = ((adx_signal[i-1] * 13) +
                         dx_signal[i]) / float(interval)

    signal['di_+'] = di_p
    signal['di_-'] = di_n
    signal['adx'] = adx_signal
    signal['high_trend'] = [HIGH_TREND] * len(adx_signal)
    signal['no_trend'] = [NO_TREND] * len(adx_signal)
    signal['strong_trend'] = [STRONG_TREND] * len(adx_signal)

    plots = [
        signal['no_trend'],
        signal['high_trend'],
        signal['strong_trend'],
        signal['adx']
    ]

    name2 = INDEXES.get(name, name)
    title = f"{name2} - Average Directional Index (ADX)"

    if plot_output:
        dual_plotting(fund['Close'],
                      plots,
                      'Price',
                      ['No Trend', 'Over Trend',
                       'Strong Trend', 'ADX'],
                      title=title)
    else:
        filename = os.path.join(name, view, f"adx_tabular_{name}.png")
        dual_plotting(fund['Close'],
                      plots,
                      'Price',
                      ['No Trend', 'Over Trend',
                       'Strong Trend', 'ADX'],
                      title=title,
                      saveFig=True,
                      filename=filename)

    return signal
