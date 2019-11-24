import pandas as pd 
import numpy as np 
from datetime import datetime

from .moving_average import simple_ma_list, exponential_ma_list, windowed_ma_list
from libs.utils import generic_plotting, dual_plotting, bar_chart
from libs.utils import dates_extractor_list

def generate_obv_signal(fund: pd.DataFrame, plot_output=True, filter_factor: float=2.5, name='') -> list:

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
    obv_slope = []
    obv_diff = [ob - obv_sig[i] for i, ob in enumerate(obv)]
        
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

    ofilter_agg = []
    ofilter_agg.append(ofilter[0])
    for i in range(1, len(ofilter)):
        ofilter_agg.append(ofilter_agg[i-1] + ofilter[i])
    # ofilter_agg_ma = simple_ma_list(ofilter, interval=91)

    x = dates_extractor_list(fund)
    name2 = name + ' - On Balance Volume'
    if plot_output:
        dual_plotting(fund['Close'], obv, x=x, y1_label='Position Price', y2_label='On Balance Volume', x_label='Trading Days', title=name2)
        dual_plotting(fund['Close'], ofilter, x=x, y1_label='Position Price', y2_label='OBV-DIFF', x_label='Trading Days', title=name2)
    else:
        filename = name +'/obv_{}.png'.format(name)
        # filename2 = name +'/obv2_{}.png'.format(name)
        # dual_plotting(fund['Close'], ofilter_agg_ma, x=x, y1_label='Position Price', y2_label='OBV-DIFF', x_label='Trading Days', title=name2, saveFig=True, filename=filename2)
        bar_chart(ofilter, x_=x, position=fund, name=name2, saveFig=True, filename=filename)

    return obv, ofilter



def on_balance_volume(fund: pd.DataFrame, plot_output=True, filter_factor: float=5.0, name='') -> dict:
    _, ofilter = generate_obv_signal(fund, plot_output=plot_output, filter_factor=filter_factor, name=name)
    dates = [index.strftime('%Y-%m-%d') for index in fund.index] 
    
    # fund_wma = windowed_ma_list(list(fund['Close']), interval=6)
    # obv_wma = windowed_ma_list(obv, interval=6)

    # TODO: (?) apply trend analysis to find divergences
    obv_dict = dict()
    obv_dict['tabular'] = ofilter
    obv_dict['dates'] = dates

    return obv_dict 

