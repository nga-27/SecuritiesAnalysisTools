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



