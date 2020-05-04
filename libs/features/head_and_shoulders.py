import pandas as pd
import numpy as np

from libs.utils import shape_plotting, generic_plotting, ProgressBar
from libs.tools import exponential_moving_avg, windowed_moving_avg

from .feature_utils import add_daterange, remove_duplicates, reconstruct_extrema, remove_empty_keys
from .feature_utils import find_filtered_local_extrema, feature_plotter, cleanse_to_json


def feature_detection_head_and_shoulders(fund: pd.DataFrame, **kwargs) -> dict:
    """Feature Detection Head and Shoulders

    PUBLIC FUNCTION: Complete detection of n sizes and features.

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    optional args:
        name {list} -- (default: {''})
        plot_output {bool} -- (default: {True})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- (default: {''})

    returns:
        dict -- head-shoulders data object
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar = kwargs.get('progress_bar', None)
    view = kwargs.get('view', '')

    head_shoulders = []
    shapes = []

    FILTER = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10,
              11, 13, 14, 16, 17, 19, 26, 35, 51]
    increment = 1.0 / float(len(FILTER)+1)

    for filt in FILTER:
        d_temp = {'filter_size': filt, "content": {}}
        hs2, _, shapes = feature_head_and_shoulders(
            fund, FILTER_SIZE=filt, name=name, shapes=shapes)
        d_temp['content'] = hs2
        d_temp = cleanse_to_json(d_temp)
        head_shoulders.append(d_temp)
        if progress_bar is not None:
            progress_bar.uptick(increment=increment)

    feature_plotter(fund, shapes, name=name,
                    feature='head_and_shoulders', plot_output=plot_output, view=view)
    if progress_bar is not None:
        progress_bar.uptick(increment=increment)

    head_shoulders = {'data': head_shoulders}
    head_shoulders['type'] = 'feature'

    return head_shoulders


def find_head_shoulders(extrema: dict, fund: pd.DataFrame) -> dict:
    """Find Head and Shoulders

    Head and shoulders detection algorithm 

    For bearish, find 3 maxima alternated by 2 minima. The 2nd maximum must be higher 
    than the other 2 maxima. For bullish, the exact opposite.

    Arguments:
        extrema {dict} -- extrema data object
        fund {pd.DataFrame} -- fund dataset

    Returns:
        dict -- extrema data object with head and shoulders content
    """
    extrema['features'] = []
    lmax = len(extrema['max'])
    lmin = len(extrema['min'])
    i = 0
    j = 0

    # indexes for potential features
    feature = []

    while (i < lmax) or (j < lmin):

        if (i < lmax) and (j < lmin):
            if extrema['max'][i][0] < extrema['min'][j][0]:
                feature.append([extrema['max'][i][0], extrema['max']
                                [i][1], fund['Volume'][extrema['max'][i][0]]])
                i += 1
            else:
                feature.append([extrema['min'][j][0], extrema['min']
                                [j][1], fund['Volume'][extrema['min'][j][0]]])
                j += 1

        elif (j < lmin):
            feature.append([extrema['min'][j][0], extrema['min']
                            [j][1], fund['Volume'][extrema['min'][j][0]]])
            j += 1

        elif (i < lmax):
            feature.append([extrema['max'][i][0], extrema['max']
                            [i][1], fund['Volume'][extrema['max'][i][0]]])
            i += 1

        else:
            break

        if len(feature) > 6:
            feature.pop(0)

        if len(feature) == 6:
            extrema['features'].append(feature_detection(feature))

    return extrema


def feature_detection(features: list) -> dict:
    """Feature Detection

    Continuation of 'find_head_shoulders' above. If feature detected, add various feature
    details as well.

    Arguments:
        features {list} -- list of features objects

    Returns:
        dict -- detected feature object (if any)
    """
    detected = {}

    if features[0][1] > features[1][1]:
        # potential TOP ('W') case (bearish)
        m1 = features[0][1]
        n1 = features[1][1]
        vol_L = features[0][2]

        if (features[2][1] > m1) and (features[2][1] > n1):
            m2 = features[2][1]
            n2 = features[3][1]
            vol_T = features[2][2]

            if (features[4][1] < m2) and (features[4][1] > n2) and (features[4][2] < vol_L):
                # m3 = features[4][1]
                # n3 = features[5][1]
                # vol_R = features[4][2]
                neckline = {'slope': 0.0, 'intercept': 0.0}
                slope = (n2 - n1) / float(features[3][0] - features[1][0])
                neckline['slope'] = float(slope)
                intercept = n1 - slope * float(features[1][0])
                neckline['intercept'] = float(intercept)
                line = neckline['intercept'] + \
                    neckline['slope'] * float(features[5][0])

                if features[5][1] < line:
                    # Head and shoulders -> bearish
                    detected['type'] = 'bearish'
                    # {'slope': 0.0, 'intercept': 0.0}
                    detected['neckline'] = neckline
                    detected['indexes'] = features.copy()
                    detected['stats'] = {
                        'width': 0, 'avg': 0.0, 'stdev': 0.0, 'percent': 0.0}
                    detected['stats']['width'] = features[4][0] - \
                        features[0][0]

                    f = features.copy()
                    f = [f[i][1] for i in range(len(f))]
                    detected['stats']['avg'] = float(np.round(np.mean(f), 3))
                    detected['stats']['stdev'] = float(np.round(np.std(f), 3))
                    detected['stats']['percent'] = float(
                        np.round(100.0 * np.std(f) / np.mean(f), 3))

    else:
        # potential BOTTOM ('M') case (bullish)
        m1 = features[0][1]
        n1 = features[1][1]
        vol_L = features[0][2]

        if (features[2][1] < m1) and (features[2][1] < n1):
            m2 = features[2][1]
            n2 = features[3][1]
            vol_T = features[3][2]

            if (features[4][1] > m2) and (features[4][1] < n2) and (vol_T > vol_L):
                # m3 = features[4][1]
                # n3 = features[5][1]
                # vol_R = features[4][2]
                neckline = {'slope': 0.0, 'intercept': 0.0}
                slope = (n2 - n1) / float(features[3][0] - features[1][0])
                neckline['slope'] = float(slope)
                intercept = n1 - slope * float(features[1][0])
                neckline['intercept'] = float(intercept)
                line = neckline['intercept'] + \
                    neckline['slope'] * float(features[5][0])

                if (features[5][1] > line) and (features[5][2] > vol_T):
                    # Head and shoulders -> bullish
                    detected['type'] = 'bullish'
                    detected['neckline'] = {'slope': 0.0, 'intercept': 0.0}
                    slope = (n2 - n1) / float(features[3][0] - features[1][0])
                    detected['neckline']['slope'] = slope
                    intercept = n1 - slope * float(features[1][0])
                    detected['neckline']['intercept'] = intercept
                    detected['indexes'] = features.copy()
                    detected['stats'] = {
                        'width': 0, 'avg': 0.0, 'stdev': 0.0, 'percent': 0.0}
                    detected['stats']['width'] = features[4][0] - \
                        features[0][0]

                    f = features.copy()
                    f = [f[i][1] for i in range(len(f))]
                    detected['stats']['avg'] = np.round(np.mean(f), 3)
                    detected['stats']['stdev'] = np.round(np.std(f), 3)
                    detected['stats']['percent'] = np.round(
                        100.0 * np.std(f) / np.mean(f), 3)

    return detected


def feature_head_and_shoulders(fund: pd.DataFrame,
                               shapes: list,
                               FILTER_SIZE=10,
                               sanitize_dict=True,
                               name='') -> list:
    """Feature Head and Shoulders

    Find head and shoulders feature of a reversal

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        shapes {list} -- list of shape objects

    Keyword Arguments:
        FILTER_SIZE {int} -- period of exponential moving average filter
        sanitize_dict {bool} -- removes min/max lists so only feature-detected elements remain
                                (default: {True})
        name {str} -- (default: {''})

    Returns:
        list -- dict of head shoulder features, moving average of fund, shapes
    """
    # Filter and find extrema. Reconstruct where those extremes exist on the actual signal.

    # ma = exponential_ma(fund, FILTER_SIZE)
    ma = windowed_moving_avg(fund, interval=FILTER_SIZE)
    if FILTER_SIZE == 0:
        ex = find_filtered_local_extrema(ma, raw=True)
    else:
        ex = find_filtered_local_extrema(ma)
    r = reconstruct_extrema(fund, ex, FILTER_SIZE, ma_type='windowed')

    # Cleanse data sample for duplicates and errors
    r = remove_duplicates(r)

    # Run detection algorithm (head and shoulders in this case)
    hs = find_head_shoulders(r, fund)

    # Cleanse data dictionary [again] and add dates for plotting features.
    hs = add_daterange(fund, hs, 5)
    hs = remove_empty_keys(hs)

    if sanitize_dict:
        hs.pop('max')
        hs.pop('min')

    if hs['features'] != []:
        for feat in hs['features']:
            fe = {}
            fe['type'] = feat['type']
            fe['indexes'] = feat['indexes']
            shapes.append(fe)

    return hs, ma, shapes
