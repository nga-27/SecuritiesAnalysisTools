import pandas as pd 
import numpy as np 

from .math_functions import lower_low, higher_high, bull_bear_th
from libs.utils import dual_plotting, date_extractor

def generate_ultimate_osc_signal(position: pd.DataFrame, config: list=[7, 14, 28]) -> list:
    """ Generate an ultimate oscillator signal from a position fund """

    bp = []
    tr = []
    ushort = []
    umed = []
    ulong = []

    ult_osc = []
    stats = position 
    
    # Mutual funds tickers update daily, several hours after close. To accomodate for any pulls of 
    # data at any time, we must know that the last [current] index may not be 'None' / 'nan'. Update
    # length of plotting to accomodate.
    tot_len = len(stats['Close'])
    if pd.isna(stats['Close'][tot_len-1]):
        tot_len -= 1

    # Generate the ultimate oscillator values
    for i in range(tot_len):
        
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
            if shtr == 0.0:
                ushort.append(0.0)
            else:
                ushort.append(np.round(shbp / shtr, 6))

        if i < config[1]:
            umed.append(0.0)
        else:
            shbp = 0.0
            shtr = 0.0
            for j in range(config[1]):
                shbp += bp[len(bp)-1-j]
                shtr += tr[len(tr)-1-j]
            if shtr == 0.0:
                umed.append(0.0)
            else:
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

    # Mutual funds tickers update daily, several hours after close. To accomodate for any pulls of 
    # data at any time, we must know that the last [current] index may not be 'None' / 'nan'. Update
    # length of plotting to accomodate.
    tot_len = len(stats['Close'])
    if pd.isna(stats['Close'][tot_len-1]):
        tot_len -= 1

    for i in range(tot_len):

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
                        trigger.append(["BULLISH", date_extractor(stats.index[start_ind], _format='str'), stats['Close'][start_ind], start_ind])
        
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
                        trigger.append(["BEARISH", date_extractor(stats.index[start_ind], _format='str'), stats['Close'][start_ind], start_ind])

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
        plots.append(0.0)
    present = False
    for i in range(len(trigger)):
        for j in range(len(simplified)):
            if simplified[j][3] == trigger[i][3]:
                present = True
        if not present:
            simplified.append(trigger[i])
            if trigger[i][0] == "BEARISH":
                plots[trigger[i][3]] = 1.0 
                ultimate['bearish'].append([trigger[i][1], trigger[i][2], trigger[i][3]])
            else:
                plots[trigger[i][3]] = -1.0
                ultimate['bullish'].append([trigger[i][1], trigger[i][2], trigger[i][3]])
        present = False 

    return [plots, ultimate]



def ultimate_oscillator(position: pd.DataFrame, name='', config: list=[7, 14, 28], plot_output=True, out_suppress=True) -> dict:
    """ Ultimate stoch: [(4 * Avg7 ) + (2 * Avg14) + (1 * Avg28)] / 7

            Avg(x) = BP(x) / TR(x)
            BP(x) = sum(close - floor[period low OR prior close]) for x days
            TR(x) = sum()
    """
    stats = position
    ult_osc = generate_ultimate_osc_signal(stats, config=config)

    trigger = ult_osc_find_triggers(stats, ult_osc)

    plots, ultimate = ult_osc_output(trigger, len(stats['Close']))
    ultimate['tabular'] = ult_osc

    #nasit_signal = nasit_oscillator_signal(ultimate, plots)
    #ultimate['nasit'] = nasit_oscillator_score(ultimate, plots)

    if not out_suppress:
        name2 = name + ' - Ultimate Oscillator'
        if plot_output:
            dual_plotting(stats['Close'], ult_osc, 'Position Price', 'Ultimate Oscillator', 'Trading Days', title=name2)
            dual_plotting(stats['Close'], plots, 'Position Price', 'Buy-Sell Signal', 'Trading Days', title=name2)
            #dual_plotting(position['Close'], clusters_wma, 'price', 'clustered oscillator', 'trading days', title=name)
            #dual_plotting(position['Close'], nasit_signal, 'price', 'clustered nasit', 'trading days', title=name)
        else:
            filename = name +'/ultimate_osc_{}.png'.format(name)
            dual_plotting(stats['Close'], ult_osc, 'Position Price', 'Ultimate Oscillator', 'Trading Days', title=name2, saveFig=True, filename=filename)
            dual_plotting(stats['Close'], plots, 'Position Price', 'Buy-Sell Signal', 'Trading Days', title=name2, saveFig=True, filename=filename)

    return ultimate
