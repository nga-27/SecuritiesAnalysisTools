import pandas as pd 
import numpy as np 

from .moving_average import simple_ma_list, exponential_ma_list
from libs.utils import generic_plotting, dual_plotting

def generate_obv_signal(fund: pd.DataFrame, plotting=True) -> list:

    obv = []

    obv.append(0.0)
    for i in range(1, len(fund['Close'])):
        if fund['Close'][i] > fund['Close'][i-1]:
            obv.append(obv[i-1] + fund['Volume'][i])
        elif fund['Close'][i] == fund['Close'][i-1]:
            obv.append(obv[i-1])
        else:
            obv.append(obv[i-1] - fund['Volume'][i])

    obv_sig = simple_ma_list(obv, interval=9)
    obv_diff = []
    obv_slope = []

    for i in range(len(obv)):
        obv_diff.append(obv[i] - obv_sig[i])
        
    omax = np.max(np.abs(obv_diff))
    ofilter = []
    for i in range(len(obv_diff)):
        if obv_diff[i] > omax / 2.0:
            ofilter.append(obv_diff[i])
        elif obv_diff[i] < (-1 * omax) / 2.0:
            ofilter.append(obv_diff[i])
        else:
            ofilter.append(0.0)

    obv_slope.append(0.0)
    for i in range(1, len(obv)):
        obv_slope.append(obv[i] - obv[i-1])

    slope_ma = exponential_ma_list(obv_slope, interval=3)
    slope_diff = []
    for i in range(len(slope_ma)):
        slope_diff.append(obv_slope[i] - slope_ma[i])

    if plotting:
        generic_plotting([obv, obv_sig], title='OBV')
        dual_plotting(fund['Close'], ofilter, 'price', 'OBV-DIFF', 'trading days')

    return obv, ofilter




    