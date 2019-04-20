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