import pandas as pd 
import numpy as np 

from libs.tools import exponential_ma_list, windowed_ma_list
from .plotting import generic_plotting

def nasit_oscillator_signal(osc_obj: dict, osc_signal: list, interval=4) -> list:
    """ Generates nasit signal from an oscillator object """
    nasit = []
    osc_raw = [(x-50.0)/100.0 for x in osc_obj['tabular']]

    tick_count = [0, 0.0]
    for i in range(interval-1):
        nasit.append(0.0)
    for i in range(interval-1, len(osc_raw)):
        if osc_signal[i] != 0.0:
            nasit.append(osc_signal[i])
        else:
            val = osc_raw[i]
            m_ema = []
            for j in range(tick_count[0]):
                m_ema.append(tick_count[1])
            for j in range(tick_count[0], interval-1):
                m_ema.append(nasit[len(nasit)-1-(interval-1-j)])
            m_ema.append(val)
            m_ema = exponential_ma_list(m_ema, interval=interval)
            nasit.append(m_ema[len(m_ema)-1])
            tick_count[0] -= 1
            if tick_count[0] < 0:
                tick_count[0] = 0

    nasit_flip = [x*-1.0 for x in nasit]
    nasit_ema = exponential_ma_list(nasit_flip, interval=3)
    #generic_plotting([nasit_ema], title='Nasit of osc') 
    return nasit_ema


def nasit_oscillator_score(osc_obj: dict, osc_signal: list) -> dict:
    if osc_signal[len(osc_signal)-1] == 1.0:
        return {'true': -1.0, 'normalized': -1.0}
    elif osc_signal[len(osc_signal)-1] == -1.0:
        return {'true': -1.0, 'normalized': -1.0}
    else:
        signal = nasit_oscillator_signal(osc_obj, osc_signal)
        sig_max = np.max(np.abs(signal))
        sig_norm = signal[len(signal)-1] / sig_max
        return {'true': signal[len(signal)-1], 'normalized': sig_norm}


def nasit_cluster_signal(cl_signal: list, interval=3) -> list:
    sig_max = np.max(np.abs(cl_signal))
    signal = [float(x) / sig_max for x in cl_signal]
    signal = [-1.0 * x for x in signal]

    nasit = windowed_ma_list(signal, interval=interval)
    #generic_plotting(nasit)
    return nasit


def nasit_cluster_score(cl_signal: list) -> dict:
    signal = nasit_cluster_signal(cl_signal)
    sig_max = np.max(np.abs(signal))
    sig_norm = signal[len(signal)-1] / sig_max

    return {'true': signal[len(signal)-1], 'normalized': sig_norm}


def nasit_composite_index(fund: pd.DataFrame) -> list:
    """ weighted? index of all nasit scores """
    from libs.tools import export_macd_nasit_signal
    composite = []


    return composite
