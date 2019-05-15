import pandas as pd 
import numpy as np 

from libs.utils import dual_plotting #nasit_oscillator_score, nasit_oscillator_signal


def generate_rsi_signal(position: pd.DataFrame, period: int=14) -> list:
    """ Generates a list of relative strength indicators """
    PERIOD = period
    change = []
    change.append(0.0)
    for i in range(1, len(position['Close'])):
        per = (position['Close'][i] - position['Close'][i-1]) / position['Close'][i-1] * 100.0
        change.append(np.round(per, 6))

    RSI = []
    # gains, losses, rs
    RS = []

    for i in range(0, PERIOD):
        RSI.append(50.0)
        RS.append([0.0, 0.0, 1.0])

    # Calculate RS for all future points
    for i in range(PERIOD, len(change)):
        pos = 0.0
        neg = 0.0
        for j in range(i-PERIOD, i):
            if change[j] > 0.0:
                pos += change[j]
            else:
                neg += np.abs(change[j])
        
        if i == PERIOD:
            rs = np.round(pos / neg, 6)
            RS.append([np.round(pos/float(PERIOD), 6), np.round(neg/float(PERIOD), 6), rs])
        else:
            if change[i] > 0.0:
                rs = (((RS[i-1][0] * float(PERIOD-1)) + change[i]) / float(PERIOD)) / (((RS[i-1][1] * float(PERIOD-1)) + 0.0) / float(PERIOD))
            else:
                rs = (((RS[i-1][0] * float(PERIOD-1)) + 0.00) / float(PERIOD)) / (((RS[i-1][1] * float(PERIOD-1)) + np.abs(change[i])) / float(PERIOD))
            RS.append([np.round(pos/float(PERIOD), 6), np.round(neg/float(PERIOD), 6), rs])

        rsi = 100.0 - (100.0 / (1.0 + RS[i][2]))
        RSI.append(np.round(rsi, 6))
    
    return RSI



def determine_rsi_swing_rejection(position: pd.DataFrame, rsi_signal: list) -> dict:
    """ Find bullish / bearish and RSI indicators:

        1. go beyond threshold
        2. go back within thresholds
        3. have local minima/maxima inside thresholds
        4. exceed max/min (bull/bear) of previous maxima/minima
    """

    LOW_TH = 30.0
    HIGH_TH = 70.0

    swings = {}
    swings['bullish'] = []
    swings['bearish'] = []
    indicator = []

    state = 0
    minima = 0.0
    maxima = 0.0
    for i in range(len(rsi_signal)):
        
        if (state == 0) and (rsi_signal[i] < LOW_TH):
            # Start of a bullish signal
            state = 1
            indicator.append(0.0)
        elif (state == 1) and (rsi_signal[i] > LOW_TH):
            state = 2
            maxima = rsi_signal[i]
            indicator.append(0.0)
        elif (state == 2):
            if rsi_signal[i] >= maxima:
                maxima = rsi_signal[i]
            else:
                minima = rsi_signal[i]
                state = 3
            indicator.append(0.0)
        elif (state == 3):
            if rsi_signal[i] < LOW_TH:
                # Failed attempted breakout
                state = 1
            if rsi_signal[i] < minima:
                minima = rsi_signal[i]
            else:
                state = 4
            indicator.append(0.0)
        elif (state == 4):
            if rsi_signal[i] > maxima:
                # Have found a bullish breakout!
                swings['bullish'].append([position.index[i], position['Close'][i], i])
                state = 0
                minima = 0.0
                maxima = 0.0 
                indicator.append(-1.0)
            else:
                indicator.append(0.0)


        elif (state == 0) and (rsi_signal[i] > HIGH_TH):
            state = 5
            indicator.append(0.0)
        elif (state == 5) and (rsi_signal[i] < HIGH_TH):
            state = 6
            minima = rsi_signal[i]
            indicator.append(0.0)
        elif (state == 6):
            if rsi_signal[i] <= minima:
                minima = rsi_signal[i]
            else:
                maxima = rsi_signal[i]
                state = 7
            indicator.append(0.0)
        elif (state == 7):
            if rsi_signal[i] > HIGH_TH:
                # Failed attempted breakout
                state = 5
            if rsi_signal[i] > maxima:
                maxima = rsi_signal[i]
            else:
                state = 8
            indicator.append(0.0)
        elif (state == 8):
            if rsi_signal[i] < minima:
                swings['bearish'].append([position.index[i], position['Close'][i], i])
                state = 0
                minima = 0.0
                maxima = 0.0
                indicator.append(1.0)
            else:
                indicator.append(0.0)

        else:
            indicator.append(0.0)

    return [indicator, swings]



def RSI(position: pd.DataFrame, name='', plot_output=True, period: int=14) -> dict:
    """ Relative Strength Indicator """
    RSI = generate_rsi_signal(position, period=period)

    plotting, rsi_swings = determine_rsi_swing_rejection(position, RSI)
    rsi_swings['tabular'] = RSI

    #print(plotting)
    #nasit_signal = nasit_oscillator_signal(rsi_swings, plotting)
    #rsi_swings['nasit'] = nasit_oscillator_score(rsi_swings, plotting)

    if plot_output:
        dual_plotting(position['Close'], RSI, 'price', 'RSI', 'trading days', title=name)
        dual_plotting(position['Close'], plotting, 'price', 'RSI indicators', 'trading days', title=name)
        #dual_plotting(position['Close'], nasit_signal, 'price', 'RSI indicators', 'trading days', title=name)

    return rsi_swings
