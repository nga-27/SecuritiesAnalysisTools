import os
from datetime import datetime
import pandas as pd
import numpy as np

from .moving_average import simple_moving_avg, exponential_moving_avg
from libs.utils import generic_plotting, dual_plotting, bar_chart
from libs.utils import dates_extractor_list, ProgressBar, SP500
from .trends import get_trendlines, get_trendlines_regression


def on_balance_volume(fund: pd.DataFrame, **kwargs) -> dict:
    """On Balance Volume

    Measure of cumulative relative change in volume. It is an indirect measure of leading momentum
    in buys and sells.

    Arguments:
        fund {pd.DataFrame} -- fund historical data

    Optional Args:
        name {str} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        filter_factor {float} -- divisor of absolute max of signal to filter out (only sig signals
                                passed) (default: {5.0})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- (default: {''})

    Returns:
        obv_dict {dict} -- contains all obv information
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    filter_factor = kwargs.get('filter_factor', 5.0)
    progress_bar = kwargs.get('progress_bar', None)
    view = kwargs.get('view', '')

    obv_dict = generate_obv_content(
        fund,
        plot_output=plot_output,
        filter_factor=filter_factor,
        name=name,
        progress_bar=progress_bar,
        view=view)

    dates = [index.strftime('%Y-%m-%d') for index in fund.index]
    obv_dict['dates'] = dates

    # Apply trend analysis to find divergences
    trend_data = dict()
    trend_data['Close'] = obv_dict['obv']
    trend_data['index'] = fund.index
    trend_data2 = pd.DataFrame.from_dict(trend_data)
    trend_data2.set_index('index', inplace=True)

    sub_name = f"obv3_{name}"
    max_window = int(len(fund['Close']) / 4)
    obv_dict['trends'] = get_trendlines(
        trend_data2, name=name,
        sub_name=sub_name,
        plot_output=plot_output,
        view=view,
        out_suppress=(not plot_output),
        interval=[0, 2, 4, 7],
        trend_window=[3, 15, 31, max_window])

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    obv = obv_dict['obv']
    if obv[0] != 0.0 and obv[2] != 0.0 and obv[5] != 0.0:
        get_trendlines_regression(obv)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.25)

    # obv_dict['trends'] = dict()
    # sub_name = f"obv_{name}"
    # obv_dict['trends']['short'] = get_trendlines(data2, name=name, sub_name=sub_name, plot_output=plot_output, interval=[2,4,7,11])
    # sub_name = f"obv_{name}_medium"
    # obv_dict['trends']['long'] = get_trendlines(data2, name=name, sub_name=sub_name, plot_output=plot_output, interval=[8,14,22,32])
    # sub_name = f"obv_{name}_long"
    # obv_dict['trends']['long'] = get_trendlines(data2, name=name, sub_name=sub_name, plot_output=plot_output, interval=[30,48,68,90])

    obv_dict['type'] = 'trend'

    return obv_dict


def generate_obv_content(fund: pd.DataFrame, **kwargs) -> dict:
    """Generate On Balance Signal Content

    Arguments:
        fund {pd.DataFrame}

    Optional Args:
        plot_output {bool} -- (default: {True})
        filter_factor {float} -- threshold divisor (x/filter_factor) for "significant" OBVs
                                (default: {2.5})
        sma_interval {int} -- interval for simple moving average (default: {20})
        name {str} -- (default: {''})
        progress_bar {ProgressBar} -- (default: {None})
        view {'str'} -- period (default: {None})

    Returns:
        dict -- obv data object
    """
    plot_output = kwargs.get('plot_output', True)
    filter_factor = kwargs.get('filter_factor', 2.5)
    sma_interval = kwargs.get('sma_interval', 20)
    name = kwargs.get('name', '')
    progress_bar = kwargs.get('progress_bar')
    view = kwargs.get('view')

    obv_dict = dict()

    obv = generate_obv_signal(fund)
    obv_dict['obv'] = obv

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    ofilter, features = obv_feature_detection(
        obv, fund, sma_interval=sma_interval,
        filter_factor=filter_factor, progress_bar=progress_bar, plot_output=plot_output)

    obv_dict['tabular'] = ofilter
    obv_dict['signals'] = features

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
                      y2_label='OBV-DIFF', x_label='Trading Days', title=name4)
        bar_chart(volume, x=x, position=fund, title=name5, all_positive=True)

    else:
        filename = os.path.join(name, view, f"obv_diff_{name}.png")
        filename2 = os.path.join(name, view, f"obv_standard_{name}.png")
        filename3 = os.path.join(name, view, f"volume_{name}.png")

        bar_chart(volume, x=x, position=fund, title=name5,
                  saveFig=True, filename=filename3, all_positive=True)
        bar_chart(ofilter, x=x, position=fund, title=name4,
                  saveFig=True, filename=filename)
        dual_plotting(fund['Close'], obv, x=x,
                      y1_label='Position Price',
                      y2_label='On Balance Volume',
                      x_label='Trading Days', title=name2,
                      saveFig=True, filename=filename2)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.125)

    obv_dict['length_of_data'] = len(obv_dict['tabular'])

    return obv_dict


def generate_obv_signal(fund: pd.DataFrame) -> list:
    """Generate On Balance Value Signal

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Returns:
        list -- on balance volume signal for period of fund
    """
    obv = []
    obv.append(0.0)
    for i in range(1, len(fund['Close'])):
        if fund['Close'][i] > fund['Close'][i-1]:
            obv.append(obv[i-1] + fund['Volume'][i])
        elif fund['Close'][i] == fund['Close'][i-1]:
            obv.append(obv[i-1])
        else:
            obv.append(obv[i-1] - fund['Volume'][i])

    return obv


def obv_feature_detection(obv: list, position: pd.DataFrame, **kwargs) -> list:
    """On Balance Volume Feature Detection

    Arguments:
        obv {list} -- on balance volume signal
        position {pd.DataFrame} -- fund dataset

    Optional Args:
        sma_interval {int} -- lookback of simple moving average (default: {20})
        plot_output {bool} -- (default: {True})
        filter_factor {float} -- threshold divisor (x/filter_factor) for "significant" OBVs
                                (default: {2.5})
        progress_bar {ProgressBar} -- (default: {None})

    Returns:
        list -- list of feature dictionaries
    """
    sma_interval = kwargs.get('sma_internal', 20)
    plot_output = kwargs.get('plot_output', True)
    filter_factor = kwargs.get('filter_factor', 2.5)
    progress_bar = kwargs.get('progress_bar')

    sma_interval2 = sma_interval * 2

    obv_sig = simple_moving_avg(obv, sma_interval, data_type='list')
    obv_sig2 = simple_moving_avg(obv, sma_interval2, data_type='list')
    obv_diff = [ob - obv_sig[i] for i, ob in enumerate(obv)]

    sma_features = find_obv_sma_trends(
        obv,
        [obv_sig, obv_sig2],
        [sma_interval, sma_interval2],
        position
    )

    if plot_output:
        generic_plotting(
            [obv, obv_sig, obv_sig2],
            title='OBV Signal Line',
            legend=['obv', f'sma-{sma_interval}', f"sma-{sma_interval*2}"]
        )

    if progress_bar is not None:
        progress_bar.uptick(increment=0.25)

    filter_factor2 = filter_factor / 2.0
    ofilter = generate_obv_ofilter(obv_diff, filter_factor2)
    sig_features = find_obv_sig_vol_spikes(ofilter, position)

    features = []
    for sig in sig_features:
        features.append(sig)
    for sma in sma_features:
        features.append(sma)

    ofilter = generate_obv_ofilter(obv_diff, filter_factor)

    return ofilter, features


def generate_obv_ofilter(obv_diff: list, filter_factor: float) -> list:
    """Generate On Balance Volume Filter

    Arguments:
        obv_diff {list} -- oscillator from sma [obv - obv_signal]
        filter_factor {float} -- threshold divisor (x/filter_factor) for "significant" OBVs

    Returns:
        list -- list of significant spikes/drops in volume
    """
    omax = np.max(np.abs(obv_diff))
    ofilter = []
    for i in range(len(obv_diff)):
        if obv_diff[i] > omax / filter_factor:
            ofilter.append(obv_diff[i])
        elif obv_diff[i] < (-1 * omax) / filter_factor:
            ofilter.append(obv_diff[i])
        else:
            ofilter.append(0.0)
    return ofilter


def find_obv_sma_trends(obv: list,
                        sma_lists: list,
                        interval_lists: list,
                        position: pd.DataFrame) -> list:
    """Find On Balance Volume SMA Trends

    Compare OBV against simple moving averages of the OBV

    Arguments:
        obv {list} -- on balance volume signal
        sma_lists {list} -- list of lists (simple moving averages of obv)
        interval_lists {list} -- lookback periods of sma_lists
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of trend dictionary objects
    """
    if len(sma_lists) != len(interval_lists):
        return []

    features = []
    state = 'at'
    for i, sma in enumerate(sma_lists):
        for j, ob in enumerate(obv):
            date = position.index[j].strftime("%Y-%m-%d")
            data = None

            if state == 'at':
                if ob > sma[j]:
                    state = 'above'
                    data = {
                        "type": 'bullish',
                        "value": f'sma-{interval_lists[i]} crossover',
                        "index": j,
                        "date": date
                    }
                elif ob < sma[j]:
                    state = 'below'
                    data = {
                        "type": 'bearish',
                        "value": f'sma-{interval_lists[i]} crossover',
                        "index": j,
                        "date": date
                    }

            elif state == 'above':
                if ob < sma[j]:
                    state = 'below'
                    data = {
                        "type": 'bearish',
                        "value": f'sma-{interval_lists[i]} crossover',
                        "index": j,
                        "date": date
                    }

            elif state == 'below':
                if ob > sma[j]:
                    state = 'above'
                    data = {
                        "type": 'bullish',
                        "value": f'sma-{interval_lists[i]} crossover',
                        "index": j,
                        "date": date
                    }

            if data is not None:
                features.append(data)

    return features


def find_obv_sig_vol_spikes(ofilter: list, position: pd.DataFrame) -> list:
    """Find On Balance Volume Significant Volume Spikes

    Using an "ofilter" signal, generate feature/signals content from list

    Arguments:
        ofilter {list} -- signal of significant volume spikes/drops
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of spike dictionary objects
    """
    features = []
    for i, obf in enumerate(ofilter):
        if obf > 0.0:
            date = position.index[i].strftime("%Y-%m-%d")
            data = {
                "type": 'bullish',
                "value": f"signficant spike: {int(obf)}",
                "index": i,
                "date": date
            }
            features.append(data)
    return features
