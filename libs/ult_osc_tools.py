import pandas as pd 
import numpy as np 

from .linear_regression import lower_low, higher_high, bull_bear_th

def generate_ultimate_osc_signal(position: pd.DataFrame, config: list=[7, 14, 28]) -> list:
    """ Generate an ultimate oscillator signal from a position fund """

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

    return ult_osc



def ult_osc_find_triggers(position: pd.DataFrame, ult_osc_signal: list, thresh_low=30, thresh_high=70) -> list:
    """ Find divergent signals for ultimate oscillators """

    ult_osc = ult_osc_signal
    stats = position
    LOW_TH = thresh_low
    HIGH_TH = thresh_high

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

    return trigger



def ult_osc_output(trigger: list, len_of_position: int) -> list:
    """ Simplifies signals to easy to view plot and dictionary
    Returns:
        list:
            plot (list): easy signal to plot on top of a position's price plot
            ultimate (dict): dictionary of specific information represented by 'plot' signal

    """
    ultimate = {}
    ultimate['bullish'] = []
    ultimate['bearish'] = []

    simplified = []
    plots = []
    for i in range(len_of_position):
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

    return [plots, ultimate]