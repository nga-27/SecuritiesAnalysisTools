import pandas as pd 
import numpy as np 
from .moving_average import exponential_ma, exponential_ma_list
from libs.utils import generic_plotting, bar_chart 

def generate_macd_signal(fund: pd.DataFrame) -> list:
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
    bar_chart(macd, 'MACD')

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
        macd_max = get_group_max(macd)
        if index == -1:
            index = len(macd)-1
        return macd[index] / np.abs(macd_max) * 100.0

    elif value_type == 'change':
        macd_ema = exponential_ma_list(macd, interval=3)
        macd_max = get_group_max(macd)
        val = (macd[len(macd)-1] - macd_ema[len(macd_ema)-1]) / macd_max * 100.0
        return val 
    
    else: 
        return None
        

def get_group_max(signal: list, index=-1) -> float:
    if index == -1:
        index == len(signal)-1
    if signal[len(signal)-1] > 0.0:
        state = 1
    else: 
        state = 0
    macd_max = 0.0
    if state == 1:
        i = len(signal)-1
        while (i >= 0) and (signal[i] > 0.0):
            if signal[i] > macd_max:
                macd_max = signal[i]
            i -= 1
    else:
        i = len(signal)-1
        while (i >= 0) and (signal[i] <= 0.0):
            if signal[i] < macd_max:
                macd_max = signal[i]
            i -= 1
    return np.abs(macd_max)


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
    if np.abs(intensity) > 50.0:
        if intensity > 0.0:
            return 'strongly_bullish'
        else:
            return 'strongly_bearish'
    else:
        if intensity > 0.0:
            return 'weakly_bullish'
        else:
            return 'weakly_bearish'


def get_macd_nasit_score(signal: list, macd: dict) -> float:
    """ NASIT score """
    if macd['state'] == 'crossover_bullish':
        return 1.0
    if macd['state'] == 'crossover_bearish':
        return -1.0

    nasit = plot_nasit_score(signal)
    return nasit[len(nasit)-1] / 100.0


def plot_nasit_score(signal: list, interval=6) -> list:
    nasit = []
    tick_count = [0, 0.0]
    for i in range(interval-1):
        nasit.append(0.0)
    for i in range(interval-1, len(signal)):
        if (signal[i] > 0.0) and (signal[i-1] < 0.0):
            nasit.append(100.0)
            tick_count = [interval-1, 100.0]
        elif (signal[i] < 0.0) and (signal[i-1] > 0.0):
            nasit.append(-100.0)
            tick_count = [interval-1, -100.0]
        else:
            val = get_macd_value(signal, value_type='group', index=i)
            val = val / 100.0 * 50.0
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

    #generic_plotting([nasit], title='NASIT for MACD')
    nasit_ema = exponential_ma_list(nasit, interval=3)
    generic_plotting([nasit_ema], title='NASIT for MACD')
    return nasit_ema


def mov_avg_convergence_divergence(fund: pd.DataFrame) -> dict:
    macd_sig, _ = generate_macd_signal(fund) 

    macd = {}

    macd['state'] = get_macd_state(macd_sig)
    
    macd['period_value'] = get_macd_value(macd_sig, value_type='current')
    macd['group_value'] = get_macd_value(macd_sig, value_type='group')

    macd['current_trend'] = get_macd_trend(macd_sig, trend_type='current')
    macd['group_trend'] = get_macd_trend(macd_sig, trend_type='group')

    macd['change'] = get_macd_value(macd_sig, value_type='change')

    macd['nasit'] = get_macd_nasit_score(macd_sig, macd)

    return macd

