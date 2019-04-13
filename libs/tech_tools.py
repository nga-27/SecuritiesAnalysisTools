import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

from .linear_regression import dual_plotting, higher_high, lower_low, bull_bear_th
from .sat_utils import  print_hello, name_parser
from .rsi_tools import generate_rsi_signal
from .ult_osc_tools import generate_ultimate_osc_signal, ult_osc_find_triggers, ult_osc_output

SELL_TH = 80.0
BUY_TH = 20.0

LOW_TH = 30.0
HIGH_TH = 70.0
BULL_BEAR = 50.0

def full_stochastic(position: pd.DataFrame, name='', config: list=[14, 3, 3], plot_output=True) -> dict:
    """ During a trend, increase config to avoid false signals:
        ex: downtrend, larger config will minimize false 'overbought' readings

        position:
            pd.DataFrame - ['Date', 'Open', 'Close', 'High', 'Low', 'Adj Close']

        typical configs: [14,3,3], [10,3,3], [20, 5, 5]
    """

    full_stoch = {}
    full_stoch['bullish'] = []
    full_stoch['bearish'] = []

    k1 = []
    k2 = []
    dd = []

    for i in range(config[0]-1):
        k1.append(50.0)
        k2.append(50.0)
        dd.append(50.0)

    for i in range(config[0]-1, len(position['Close'])):

        # Find first lookback of oscillator
        lows = position['Low'][i-(config[0]-1):i+1]
        highs = position['High'][i-(config[0]-1):i+1]
        low = np.min(lows)
        high = np.max(highs)

        s = [low, high, position['Close'][i]]

        K = (position['Close'][i] - low) / (high - low) * 100.0
        k1.append(K)

        # Smooth oscillator with config[1]
        k2.append(np.average(k1[i-(config[1]-1):i+1]))

        # Find 'Simple Moving Average' (SMA) of k2
        dd.append(np.average(k2[i-(config[2]-1):i+1]))

    stochastic = []
    indicator = 0 # 0 is neutral, 1,2 is oversold, 3,4: is overbought
    for i in range(len(position['Close'])):

        if k2[i] > SELL_TH:
            indicator = 3
            stochastic.append(0)
        elif (indicator == 3) and (k2[i] < dd[i]):
            indicator = 4
            stochastic.append(0)
        elif (indicator == 4) and (k2[i] < SELL_TH):
            indicator = 0
            full_stoch['bearish'].append([position['Date'][i], position['Close'][i], i])
            stochastic.append(1)

        elif k2[i] < BUY_TH:
            indicator = 1
            stochastic.append(0)
        elif (indicator == 1) and (k2[i] > dd[i]):
            indicator = 2
            stochastic.append(0)
        elif (indicator == 2) and (k2[i] > BUY_TH):
            indicator = 0
            full_stoch['bullish'].append([position['Date'][i], position['Close'][i], i])
            stochastic.append(-1)

        else:
            stochastic.append(0)
            
    if plot_output:
        dual_plotting(position['Close'], stochastic, 'Position Price', 'Oscillator Signal', title=name)

    return full_stoch



def ultimate_oscillator(position: pd.DataFrame, name='', config: list=[7, 14, 28], plot_output=True) -> dict:
    """ Ultimate stoch: [(4 * Avg7 ) + (2 * Avg14) + (1 * Avg28)] / 7

            Avg(x) = BP(x) / TR(x)
            BP(x) = sum(close - floor[period low OR prior close]) for x days
            TR(x) = sum()
    """
    stats = position
    ult_osc = generate_ultimate_osc_signal(stats, config=config)

    trigger = ult_osc_find_triggers(stats, ult_osc)

    plots, ultimate = ult_osc_output(trigger, len(stats['Close']))

    if plot_output:
        dual_plotting(stats['Close'], ult_osc, 'price', 'ultimate oscillator', 'trading days', title=name)
        dual_plotting(stats['Close'], plots, 'price', 'buy-sell signal', 'trading days', title=name)

    return ultimate



def trend_filter(osc: dict, position: pd.DataFrame) -> dict:
    """ Filters oscillator dict to remove trend bias.

        Ex: strong upward trend -> removes weaker drops in oscillators
    """
    filtered = {}

    return filtered 



def cluster_oscs(position: pd.DataFrame, name='', plot_output=True, function: str='full_stochastic', filter=7) -> list:
    """ 2-3-5-8 multiplier comparing several different osc lengths """
    THRESH = filter
    clusters = []

    for i in range(len(position)):
        clusters.append(0)

    if function == 'full_stochastic':
        fast = full_stochastic(position, config=[10,3,3], plot_output=False)
        med = full_stochastic(position, config=[14,3,3], plot_output=False)
        slow = full_stochastic(position, config=[20,5,5], plot_output=False)
    elif function == 'ultimate':
        fast = ultimate_oscillator(position, config=[4,8,16], plot_output=False)
        med = ultimate_oscillator(position, config=[5,10,20], plot_output=False)
        slow = ultimate_oscillator(position, config=[7,14,28], plot_output=False)
    else:
        print(f'Warning: Unrecognized function input of {function} in cluster_oscs.')
        return None

    clusters = clustering(clusters, fast)
    clusters = clustering(clusters, med)
    clusters = clustering(clusters, slow)

    for i in range(len(clusters)):
        if (clusters[i] < THRESH) and (clusters[i] > -THRESH):
            clusters[i] = 0
    
    if plot_output:
        dual_plotting(position['Close'], clusters, 'price', 'clustered oscillator', 'trading days', title=name)

    return clusters 



def clustering(updatable: list, evaluator: dict) -> list:
    for bull in evaluator['bullish']:
        index = bull[2]
        updatable[index] += -8 if updatable[index] != 0 else -1
        if index < len(updatable)-1:
            updatable[index-1] += -5 if updatable[index-1] != 0 else 0
            updatable[index+1] += -5 if updatable[index+1] != 0 else 0
        if index < len(updatable)-2:
            updatable[index-2] += -3 if updatable[index-2] != 0 else 0
            updatable[index+2] += -3 if updatable[index+2] != 0 else 0
        if index < len(updatable)-3:
            updatable[index-3] += -2 if updatable[index-3] != 0 else 0
            updatable[index+3] += -2 if updatable[index+3] != 0 else 0

    for bear in evaluator['bearish']:
        index = bear[2]
        updatable[index] += 8 if updatable[index] != 0 else 1
        if index < len(updatable)-1:
            updatable[index-1] += 5 if updatable[index-1] != 0 else 0
            updatable[index+1] += 5 if updatable[index+1] != 0 else 0
        if index < len(updatable)-2:
            updatable[index-2] += 3 if updatable[index-2] != 0 else 0
            updatable[index+2] += 3 if updatable[index+2] != 0 else 0
        if index < len(updatable)-3:
            updatable[index-3] += 2 if updatable[index-3] != 0 else 0
            updatable[index+3] += 2 if updatable[index+3] != 0 else 0

    return updatable



def RSI(position: pd.DataFrame, name='', plot_output=True, period: int=14):
    """ Relative Strength Indicator """
    RSI = generate_rsi_signal(position, period=period)

    if plot_output:
        dual_plotting(position['Close'], RSI, 'price', 'RSI', 'trading days', title=name)

    # TODO: conditions of rsi (divergence, etc.)