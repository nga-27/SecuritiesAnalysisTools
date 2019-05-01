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
    for i in range(interval-1):
        ema.append(item[i])
    for i in range(interval-1, len(item)):
        ema.append(np.mean(item[i-(interval-1):i+1]))
        if i != interval-1:
            ema[i] = ema[i-1] * (1.0 - k) + item[i] * k

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
