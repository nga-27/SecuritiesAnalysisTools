import pandas as pd 
import numpy as np 

from .moving_average import simple_ma_list, exponential_ma_list, windowed_ma_list
from libs.utils import generic_plotting, dual_plotting, dates_extractor_list

def generate_obv_signal(fund: pd.DataFrame, plotting=True, filter_factor: float=2.5) -> list:

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
        if obv_diff[i] > omax / filter_factor:
            ofilter.append(obv_diff[i])
        elif obv_diff[i] < (-1 * omax) / filter_factor:
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
        x = dates_extractor_list(fund)
        generic_plotting([obv, obv_sig], x_=x, title='OBV')
        dual_plotting(fund['Close'], ofilter, x=x, y1_label='price', y2_label='OBV-DIFF', x_label='trading days')

    return obv, ofilter


def on_balance_volume(fund: pd.DataFrame, plotting=True, filter_factor: float=2.5) -> list:
    obv, ofilter = generate_obv_signal(fund, plotting=plotting, filter_factor=filter_factor)
    dates = dates_extractor_list(fund) 
    
    fund_wma = windowed_ma_list(list(fund['Close']), interval=6)
    obv_wma = windowed_ma_list(obv, interval=6)

    # TODO: (?) apply trend analysis to find divergences

    if plotting:
        dual_plotting(fund_wma, obv_wma, 'price', 'window', 'trading', x=dates)
    return obv, ofilter 

