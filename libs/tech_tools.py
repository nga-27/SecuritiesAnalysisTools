import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt

from .linear_regression import dual_plotting, higher_high, lower_low, bull_bear_th
from .sat_utils import  print_hello, name_parser

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
    bp = []
    tr = []
    ushort = []
    umed = []
    ulong = []

    ult_osc = []
    stats = position 

    # Generate the ultimate oscillator values
    for i in range(len(stats['Close'])):
        
        # Handle edge cases first
        if i < 1:
            bp.append(0.0)
            tr.append(0.0)
            low = 0
            high = 0
        else:
            low = np.min([stats['Low'][i], stats['Close'][i-1]])
            high = np.max([stats['High'][i], stats['Close'][i-1]])
            bp.append(np.round(stats['Close'][i] - low, 6))
            tr.append(np.round(high - low, 6))

        if i < config[0]:
            ushort.append(0.0)
        else:
            shbp = 0.0
            shtr = 0.0
            for j in range(config[0]):
                shbp += bp[len(bp)-1-j]
                shtr += tr[len(tr)-1-j]
            ushort.append(np.round(shbp / shtr, 6))

        if i < config[1]:
            umed.append(0.0)
        else:
            shbp = 0.0
            shtr = 0.0
            for j in range(config[1]):
                shbp += bp[len(bp)-1-j]
                shtr += tr[len(tr)-1-j]
            umed.append(np.round(shbp / shtr, 6))

        if i < config[2]:
            ulong.append(0.0)
            ult_osc.append(50.0)
        else:
            shbp = 0.0
            shtr = 0.0
            for j in range(config[2]):
                shbp += bp[len(bp)-1-j]
                shtr += tr[len(tr)-1-j]
            ulong.append(np.round(shbp / shtr, 6))
            ult_osc.append(np.round(100.0 * ((4.0 * ushort[i]) + (2.0 * umed[i]) + ulong[i]) / 7.0, 6))

    ultimate = {}
    ultimate['bullish'] = []
    ultimate['bearish'] = []

    trigger = []
    marker_val = 0.0
    marker_ind = 0
    for i in range(len(stats['Close'])):

        # Find bullish signal
        if ult_osc[i] < LOW_TH:
            ult1 = ult_osc[i]
            marker_val = stats['Close'][i]
            marker_ind = i 
            lows = lower_low(stats['Close'], marker_val, marker_ind)
            if len(lows) != 0:
                ult2 = ult_osc[lows[len(lows)-1][1]]
            
                if ult2 > ult1:
                    start_ind = lows[len(lows)-1][1]
                    interval = np.max(ult_osc[i:start_ind+1])
                    start_ind = bull_bear_th(ult_osc, start_ind, interval, bull_bear='bull')
                    if start_ind is not None:
                        trigger.append(["BULLISH", stats['Date'][start_ind], stats['Close'][start_ind], start_ind])
        
        # Find bearish signal
        if ult_osc[i] > HIGH_TH:
            ult1 = ult_osc[i]
            marker_val = stats['Close'][i]
            marker_ind = i
            highs = higher_high(stats['Close'], marker_val, marker_ind)
            if len(highs) != 0:
                ult2 = ult_osc[highs[len(highs)-1][1]]

                if ult2 < ult1:
                    start_ind = highs[len(highs)-1][1]
                    interval = np.min(ult_osc[i:start_ind+1])
                    start_ind = bull_bear_th(ult_osc, start_ind, interval, bull_bear='bear')
                    if start_ind is not None:
                        trigger.append(["BEARISH", stats['Date'][start_ind], stats['Close'][start_ind], start_ind])

    simplified = []
    plots = []
    for i in range(len(stats['Close'])):
        plots.append(50.0)
    present = False
    for i in range(len(trigger)):
        for j in range(len(simplified)):
            if simplified[j][3] == trigger[i][3]:
                present = True
        if not present:
            simplified.append(trigger[i])
            if trigger[i][0] == "BEARISH":
                plots[trigger[i][3]] = 100.0
                ultimate['bearish'].append([trigger[i][1], trigger[i][2], trigger[i][3]])
            else:
                plots[trigger[i][3]] = 0.0
                ultimate['bullish'].append([trigger[i][1], trigger[i][2], trigger[i][3]])
        present = False 


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