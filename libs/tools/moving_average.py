import pandas as pd 
import numpy as np 

def exponential_ma(fund: pd.DataFrame, interval: int) -> list:
    ema = []
    k = 2.0 / (float(interval) + 1.0)
    for i in range(interval-1):
        ema.append(fund['Close'][i])
    for i in range(interval-1, len(fund['Close'])):
        ema.append(np.mean(fund['Close'][i-(interval-1):i+1]))
        if i != interval-1:
            ema[i] = ema[i-1] * (1.0 - k) + fund['Close'][i] * k

    return ema 


def exponential_ma_list(item: list, interval: int) -> list:
    ema = []
    k = 2.0 / (float(interval) + 1.0)
    if len(item) > interval:
        for i in range(interval-1):
            ema.append(item[i])
        for i in range(interval-1, len(item)):
            ema.append(np.mean(item[i-(interval-1):i+1]))
            if i != interval-1:
                ema[i] = ema[i-1] * (1.0 - k) + item[i] * k
    else:
        ema = item

    return ema 


def windowed_ma_list(item: list, interval: int) -> list:
    left = int(np.floor(float(interval) / 2))
    wma = []
    for i in range(left):
        wma.append(item[i])
    for i in range(left, len(item)-left):
        wma.append(np.mean(item[i-(left):i+1+(left)]))
    for i in range(len(item)-left, len(item)):
        wma.append(item[i])

    return wma 


def simple_ma_list(item: list, interval: int) -> list:
    ma = []
    for i in range(interval-1):
        ma.append(item[i])
    for i in range(interval-1, len(item)):
        av = np.mean(item[i-(interval-1):i+1])
        ma.append(av)

    return ma 



def triple_moving_average(fund: pd.DataFrame, config=[12, 50, 200], plotting=True) -> list:
    from libs.utils import generic_plotting

    tshort = []
    tmed = []
    tlong = []

    tot_len = len(fund['Close'])

    for i in range(config[0]):
        tshort.append(fund['Close'][i])
        tmed.append(fund['Close'][i])
        tlong.append(fund['Close'][i])
    for i in range(config[0], config[1]):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(fund['Close'][i])
        tlong.append(fund['Close'][i])
    for i in range(config[1], config[2]):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(np.mean(fund['Close'][i-config[1]:i+1]))
        tlong.append(fund['Close'][i])
    for i in range(config[2], tot_len):
        tshort.append(np.mean(fund['Close'][i-config[0]:i+1]))
        tmed.append(np.mean(fund['Close'][i-config[1]:i+1]))
        tlong.append(np.mean(fund['Close'][i-config[2]:i+1]))

    if plotting:
        generic_plotting([fund['Close'], tshort, tmed, tlong])

    return tshort, tmed, tlong