import pandas as pd 
import numpy as np 


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