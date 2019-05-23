import pandas as pd 
import numpy as np 

from .moving_average import exponential_ma, exponential_ma_list
from libs.utils import generic_plotting, bar_chart, dual_plotting, dates_extractor_list

"""
Moving Average Convergence / Divergence (MACD)
    * macd = EMA(12) - EMA(26)
    * macd_val = macd - macd_EMA(9)
    
    * "trend-following momentum indicator"

    TODO: speed of crossovers can be a signal of overbought / oversold 
"""

def generate_macd_signal(fund: pd.DataFrame, plotting=True, name='') -> list:
    """
    macd = ema(12) - ema(26)
    'signal' = macd(ema(9))
    """
    emaTw = exponential_ma(fund, interval=12)
    emaTs = exponential_ma(fund, interval=26)
    macd = []

    for i in range(len(emaTw)):
        macd.append(emaTw[i] - emaTs[i])

    macd_ema = exponential_ma_list(macd, interval=9)
    x = dates_extractor_list(fund)
    name2 = name + ' - MACD'
    if plotting:
        bar_chart(macd, x_=x, name=name2)
    else:
        filename = name + '/macd_bar_{}.png'.format(name)
        bar_chart(macd, x_=x, name=name2, saveFig=True, filename=filename)

    return macd, macd_ema


def get_macd_trend(macd: list, trend_type: str='current') -> str:
    if trend_type == 'current':
        if macd[len(macd)-1] > macd[len(macd)-2]:
            return 'rising'
        else:
            return 'falling'

    elif trend_type == 'group':
        if macd[len(macd)-1] > 0.0:
            state = 1
        else: 
            state = 0
        if state == 1:
            i = len(macd)-1
            group_size = 0
            while (i >= 0) and (state == 1):
                if macd[i] > 0.0:
                    i -= 1
                    group_size += 1
                else:
                    state = 0
            m_ema = exponential_ma_list(macd[i:len(macd)], interval=3)
            if macd[len(macd)-1] > m_ema[len(m_ema)-1]:
                return 'rising'
            else:
                return 'falling'
        else:
            i = len(macd)-1
            group_size = 0
            while (i >= 0) and (state == 1):
                if macd[i] <= 0.0:
                    i -= 1
                    group_size += 1
                else:
                    state = 0
            m_ema = exponential_ma_list(macd[i:len(macd)], interval=3)
            if macd[len(macd)-1] > m_ema[len(m_ema)-1]:
                return 'rising'
            else:
                return 'falling'

    else:
        print("WARNING - no valid 'trend_type' provided in 'get_macd_trend'")
        return None


def get_macd_value(macd: list, value_type='current', index=-1) -> float:
    if value_type == 'current':
        macd_max = np.max(np.abs(macd))
        return macd[len(macd)-1] / macd_max * 100.0
    
    elif value_type == 'group':
        macd_max = get_group_max(macd, index=index)
        if macd_max == 0.0:
            return 0.0
        if index == -1:
            index = len(macd)-1
        return macd[index] / np.abs(macd_max) * 100.0

    elif value_type == 'change':
        macd_ema = exponential_ma_list(macd, interval=3)
        macd_max = get_group_max(macd)
        if macd_max == 0.0:
            return 0.0
        val = (macd[len(macd)-1] - macd_ema[len(macd_ema)-1]) / macd_max * 100.0
        return val 
    
    else: 
        return None


def get_group_range(signal: list, index: int) -> list:
    """ [start_index, end_index] """
    if signal[index] > 0.0:
        state = 1
    else: 
        state = 0

    start = index
    while (start >= 0):
        if state == 1:
            if signal[start] < 0.0:
                start += 1
                break
            else:
                start -= 1
        else:
            if signal[start] > 0.0:
                start += 1
                break
            else:
                start -= 1
    if start == -1:
        start = 0

    end = index
    while (end < len(signal)):
        if state == 1:
            if signal[end] < 0.0:
                end -= 1
                break
            else:
                end += 1
        else:
            if signal[end] > 0.0:
                end -= 1
                break
            else:
                end += 1

    return [start, end, (end-start+1)]
        

def get_group_max(signal: list, index=-1) -> float:
    if index == -1:
        index = len(signal)-1
    start, end, _ = get_group_range(signal, index)
    macd_max = np.max(np.abs(signal[start:end+1]))
    return macd_max


def get_group_duration_factor(signal: list, index: int, f_type='signal') -> float:
    """ normalization to crossovers of different sizes """
    if index - 2 > 0:
        index -= 2
    else:
        return 1.25
    d1 = get_group_range(signal, index)
    if d1[0] - 2 > 0:
        # 'start' variable
        d2 = get_group_range(signal, d1[0]-2)
    else:
        return 1.25

    d_max = np.max([d1[2], d2[2]])
    if f_type == 'signal':
        factor = 1.25 - (d1[2] / d_max) * 0.25
    elif f_type == 'score':
        factor = 1.1 - (d1[2] / d_max) * 0.1
    elif f_type == 'state':
        factor = 1.5 - (d1[2] / d_max) * 0.5
    else:
        return 1.0
    return factor
    


def has_crossover(signal: list, interval=3) -> str:
    if (signal[len(signal)-1] > 0.0) and (signal[len(signal)-1-interval] < 0.0):
        return 'crossover_bullish'
    elif (signal[len(signal)-1] < 0.0) and (signal[len(signal)-1-interval] > 0.0):
        return 'crossover_bearish'
    else:
        return None
    

def get_macd_state(macd: list) -> str:
    """
    states: 'strongly', 'weakly', 'crossover' + bear/bullish
    """ 
    cross = has_crossover(macd)
    if cross is not None:
        return cross 
    intensity = get_macd_value(macd, value_type='group')
    factor = get_group_duration_factor(macd, len(macd)-1, f_type='state')
    intensity = intensity / factor
    if np.abs(intensity) > 70.0:
        if intensity > 0.0:
            return 'strongly_bullish'
        else:
            return 'strongly_bearish'
    else:
        if intensity > 0.0:
            return 'weakly_bullish'
        else:
            return 'weakly_bearish'


def get_macd_nasit_score(signal: list, macd: dict) -> dict:
    """ NASIT score """
    factor = get_group_duration_factor(signal, len(signal)-1, f_type='score')
    if macd['state'] == 'crossover_bullish':
        return {'true': 1.0/factor, 'normalized': 1.0/factor}
    if macd['state'] == 'crossover_bearish':
        return {'true': -1.0/factor, 'normalized': -1.0/factor}

    nasit = get_nasit_signal(signal) 
    #print(nasit)
    na_max = np.max(np.abs(nasit))
    na_norm = nasit[len(nasit)-1] / na_max
    return {'true': nasit[len(nasit)-1] / 100.0, 'normalized': na_norm}


def get_nasit_signal(signal: list, interval=6) -> list:
    nasit = []
    tick_count = [0, 0.0]
    for i in range(interval-1):
        nasit.append(0.0)
    for i in range(interval-1, len(signal)):
        if (signal[i] > 0.0) and (signal[i-1] < 0.0):
            nasit.append(100.0)
            tick_count = [interval-1, 100.0, get_group_duration_factor(signal, i, f_type='signal')]
        elif (signal[i] < 0.0) and (signal[i-1] > 0.0):
            nasit.append(-100.0)
            tick_count = [interval-1, -100.0, get_group_duration_factor(signal, i, f_type='signal')]
        else:
            val = get_macd_value(signal, value_type='group', index=i)
            val = val / 100.0 * 50.0
            m_ema = []
            for j in range(tick_count[0]):
                m_ema.append(tick_count[1] / tick_count[2])
            for j in range(tick_count[0], interval-1):
                m_ema.append(nasit[len(nasit)-1-(interval-1-j)])
            m_ema.append(val)
            m_ema = exponential_ma_list(m_ema, interval=interval)
            nasit.append(m_ema[len(m_ema)-1])
            tick_count[0] -= 1
            if tick_count[0] < 0:
                tick_count[0] = 0

    #generic_plotting([nasit], title='NASIT for MACD')
    nasit_ema = exponential_ma_list(nasit, interval=3)
    #print(nasit_ema)
    #generic_plotting([nasit_ema], title='NASIT for MACD')
    return nasit_ema


def export_macd_nasit_signal(fund: pd.DataFrame, plotting=False) -> list: 
    macd_sig, _ = generate_macd_signal(fund, plotting=False)
    nasit = get_nasit_signal(macd_sig)
    return nasit 


def mov_avg_convergence_divergence(fund: pd.DataFrame, plot_output=False, name='') -> dict:
    macd_sig, _ = generate_macd_signal(fund, plotting=plot_output, name=name) 

    macd = {}

    macd['state'] = get_macd_state(macd_sig)
    
    macd['period_value'] = get_macd_value(macd_sig, value_type='current')
    macd['group_value'] = get_macd_value(macd_sig, value_type='group')

    macd['current_trend'] = get_macd_trend(macd_sig, trend_type='current')
    macd['group_trend'] = get_macd_trend(macd_sig, trend_type='group')

    macd['change'] = get_macd_value(macd_sig, value_type='change')

    macd['nasit'] = get_macd_nasit_score(macd_sig, macd)

    # if plot_output:
    #     #nasit = get_nasit_signal(macd_sig)
    #     #dual_plotting(fund['Close'], nasit, 'Price', 'Nasit score', 'trading')

    name2 = name + ' - MACD: '
    if plot_output:
        dual_plotting(fund['Close'], macd_sig, 'Position Price', 'MACD', 'Trading Days', title=name2)
        #dual_plotting(position['Close'], clusters_wma, 'price', 'clustered oscillator', 'trading days', title=name)
        #dual_plotting(position['Close'], nasit_signal, 'price', 'clustered nasit', 'trading days', title=name)
    else:
        filename = name +'/macd_{}.png'.format(name)
        dual_plotting(fund['Close'], macd_sig, 'Position Price', 'MACD', 'Trading Days', title=name2, saveFig=True, filename=filename)

    return macd

