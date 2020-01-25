from datetime import datetime
import pandas as pd
import numpy as np

from .moving_average import simple_moving_avg, exponential_moving_avg
from libs.utils import generic_plotting, dual_plotting, bar_chart
from libs.utils import dates_extractor_list, ProgressBar, SP500
from .trends import get_trendlines


def generate_obv_signal(fund: pd.DataFrame, **kwargs) -> list:
    """Generate On Balance Signal

    Arguments:
        fund {pd.DataFrame}

    Keyword Arguments:
        plot_output {bool} -- (default: {True})
        filter_factor {float} -- threshold divisor (x/filter_factor) for "significant" OBVs (default: {2.5})
        name {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- signal
    """
    plot_output = kwargs.get('plot_output', True)
    filter_factor = kwargs.get('filter_factor', 2.5)
    name = kwargs.get('name', '')
    progress_bar = kwargs.get('progress_bar')

    obv = []

    obv.append(0.0)
    for i in range(1, len(fund['Close'])):
        if fund['Close'][i] > fund['Close'][i-1]:
            obv.append(obv[i-1] + fund['Volume'][i])
        elif fund['Close'][i] == fund['Close'][i-1]:
            obv.append(obv[i-1])
        else:
            obv.append(obv[i-1] - fund['Volume'][i])

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    obv_sig = simple_moving_avg(obv, interval=9, data_type='list')
    obv_slope = []
    obv_diff = [ob - obv_sig[i] for i, ob in enumerate(obv)]

    if progress_bar is not None:
        progress_bar.uptick(increment=0.25)

    omax = np.max(np.abs(obv_diff))
    ofilter = []
    for i in range(len(obv_diff)):
        if obv_diff[i] > omax / filter_factor:
            ofilter.append(obv_diff[i])
        elif obv_diff[i] < (-1 * omax) / filter_factor:
            ofilter.append(obv_diff[i])
        else:
            ofilter.append(0.0)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    obv_slope.append(0.0)
    for i in range(1, len(obv)):
        obv_slope.append(obv[i] - obv[i-1])

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    slope_ma = exponential_moving_avg(obv_slope, interval=3, data_type='list')
    slope_diff = []
    for i in range(len(slope_ma)):
        slope_diff.append(obv_slope[i] - slope_ma[i])

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    ofilter_agg = []
    ofilter_agg.append(ofilter[0])
    for i in range(1, len(ofilter)):
        ofilter_agg.append(ofilter_agg[i-1] + ofilter[i])
    # ofilter_agg_ma = simple_ma_list(ofilter, interval=91)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    volume = []
    volume.append(fund['Volume'][0])
    for i in range(1, len(fund['Volume'])):
        if fund['Close'][i] - fund['Close'][i-1] < 0:
            volume.append(-1.0 * fund['Volume'][i])
        else:
            volume.append(fund['Volume'][i])

    x = dates_extractor_list(fund)
    name3 = SP500.get(name, name)
    name2 = name3 + ' - On Balance Volume (OBV)'
    name4 = name3 + ' - Significant OBV Changes'
    name5 = name3 + ' - Volume'
    if plot_output:
        dual_plotting(fund['Close'], obv, x=x, y1_label='Position Price',
                      y2_label='On Balance Volume', x_label='Trading Days', title=name2)
        dual_plotting(fund['Close'], ofilter, x=x, y1_label='Position Price',
                      y2_label='OBV-DIFF', x_label='Trading Days', title=name2)
        bar_chart(volume, x=x, position=fund, title=name5, all_positive=True)
    else:
        filename = name + '/obv_diff_{}.png'.format(name)
        filename2 = name + '/obv_standard_{}.png'.format(name)
        filename3 = name + '/volume_{}.png'.format(name)
        # dual_plotting(fund['Close'], ofilter_agg_ma, x=x, y1_label='Position Price', y2_label='OBV-DIFF', x_label='Trading Days', title=name2, saveFig=True, filename=filename2)
        bar_chart(volume, x=x, position=fund, title=name5,
                  saveFig=True, filename=filename3, all_positive=True)
        bar_chart(ofilter, x=x, position=fund, title=name4,
                  saveFig=True, filename=filename)
        dual_plotting(fund['Close'], obv, x=x, y1_label='Position Price', y2_label='On Balance Volume',
                      x_label='Trading Days', title=name2, saveFig=True, filename=filename2)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    return obv, ofilter


def on_balance_volume(fund: pd.DataFrame, **kwargs) -> dict:
    """
    On Balance Volume:  indirect measure of leading momentum in buys and sells

    args:
        fund:           (pd.DataFrame) fund historical data

    optional args:
        name:           (list) name of fund, primarily for plotting; DEFAULT=''
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        filter_factor:  (float) divisor of absolute max of signal to filter out (only sig signals passed); DEFAULT=5.0
        progress_bar:   (ProgressBar) DEFAULT=None

    returns:
        obv_dict:       (dict) contains all obv information
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    filter_factor = kwargs.get('filter_factor', 5.0)
    progress_bar = kwargs.get('progress_bar', None)

    obv, ofilter = generate_obv_signal(
        fund, plot_output=plot_output, filter_factor=filter_factor, name=name, progress_bar=progress_bar)
    dates = [index.strftime('%Y-%m-%d') for index in fund.index]

    # Apply trend analysis to find divergences
    data = dict()
    data['Close'] = obv
    data['index'] = fund.index
    data2 = pd.DataFrame.from_dict(data)
    data2.set_index('index', inplace=True)

    obv_dict = dict()
    obv_dict['tabular'] = ofilter
    obv_dict['dates'] = dates

    sub_name = f"obv3_{name}"
    obv_dict['trends'] = get_trendlines(
        data2, name=name, sub_name=sub_name, plot_output=plot_output)

    # obv_dict['trends'] = dict()
    # sub_name = f"obv_{name}"
    # obv_dict['trends']['short'] = get_trendlines(data2, name=name, sub_name=sub_name, plot_output=plot_output, interval=[2,4,7,11])
    # sub_name = f"obv_{name}_medium"
    # obv_dict['trends']['long'] = get_trendlines(data2, name=name, sub_name=sub_name, plot_output=plot_output, interval=[8,14,22,32])
    # sub_name = f"obv_{name}_long"
    # obv_dict['trends']['long'] = get_trendlines(data2, name=name, sub_name=sub_name, plot_output=plot_output, interval=[30,48,68,90])

    return obv_dict
