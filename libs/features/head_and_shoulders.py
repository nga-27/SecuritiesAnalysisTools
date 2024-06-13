""" Head And Shoulders Feature Detection"""
from typing import List, Tuple, Union

import pandas as pd
import numpy as np

from libs.utils.progress_bar import ProgressBar, update_progress_bar
from libs.tools.moving_averages_lib.windowed_moving_avg import windowed_moving_avg

from .feature_utils import (
    add_date_range, remove_duplicates, reconstruct_extrema, remove_empty_keys
)
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
    progress_bar: Union[ProgressBar, None] = kwargs.get('progress_bar')
    view = kwargs.get('view', '')

    head_shoulders = []
    shapes = []
    filter_x = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 16, 17, 19, 26, 35, 51]
    increment = 1.0 / float(len(filter_x) + 1)

    for filter_val in filter_x:
        d_temp = {'filter_size': filter_val, "content": {}}
        hs2, _, shapes = feature_head_and_shoulders(fund, filter_size=filter_val, shapes=shapes)
        d_temp['content'] = hs2
        d_temp = cleanse_to_json(d_temp)
        head_shoulders.append(d_temp)
        update_progress_bar(progress_bar, increment)

    feature_plotter(fund, shapes, name=name,
                    feature='head_and_shoulders', plot_output=plot_output, view=view)
    update_progress_bar(progress_bar, increment)

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
    len_max = len(extrema['max'])
    len_min = len(extrema['min'])
    i = 0
    j = 0

    # indexes for potential features
    feature = []

    while i < len_max or j < len_min:
        if i < len_max and j < len_min:
            if extrema['max'][i][0] < extrema['min'][j][0]:
                feature.append(
                    [
                        extrema['max'][i][0],
                        extrema['max'][i][1],
                        fund['Volume'][extrema['max'][i][0]]
                    ]
                )
                i += 1
            else:
                feature.append(
                    [
                        extrema['min'][j][0],
                        extrema['min'][j][1],
                        fund['Volume'][extrema['min'][j][0]]
                    ]
                )
                j += 1

        elif j < len_min:
            feature.append(
                [
                    extrema['min'][j][0],
                    extrema['min'][j][1],
                    fund['Volume'][extrema['min'][j][0]]
                ]
            )
            j += 1

        elif i < len_max:
            feature.append(
                [
                    extrema['max'][i][0],
                    extrema['max'][i][1],
                    fund['Volume'][extrema['max'][i][0]]
                ]
            )
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
    # pylint: disable=too-many-statements
    detected = {}
    if features[0][1] > features[1][1]:
        # potential TOP ('W') case (bearish)
        max1 = features[0][1]
        min1 = features[1][1]
        vol_low = features[0][2]

        if (features[2][1] > max1) and (features[2][1] > min1):
            max2 = features[2][1]
            min2 = features[3][1]
            vol_top = features[2][2]

            if (features[4][1] < max2) and (features[4][1] > min2) and (features[4][2] < vol_low):
                # m3 = features[4][1]
                # n3 = features[5][1]
                # vol_R = features[4][2]
                neckline = {'slope': 0.0, 'intercept': 0.0}
                slope = (min2 - min1) / float(features[3][0] - features[1][0])
                neckline['slope'] = float(slope)
                intercept = min1 - slope * float(features[1][0])
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

                    feats = features.copy()
                    feats = [feat[1] for feat in feats]
                    detected['stats']['avg'] = float(np.round(np.mean(feats), 3))
                    detected['stats']['stdev'] = float(np.round(np.std(feats), 3))
                    detected['stats']['percent'] = float(
                        np.round(100.0 * np.std(feats) / np.mean(feats), 3))

    else:
        # potential BOTTOM ('M') case (bullish)
        max1 = features[0][1]
        min1 = features[1][1]
        vol_low = features[0][2]

        if (features[2][1] < max1) and (features[2][1] < min1):
            max2 = features[2][1]
            min2 = features[3][1]
            vol_top = features[3][2]

            if (features[4][1] > max2) and (features[4][1] < min2) and (vol_top > vol_low):
                # m3 = features[4][1]
                # n3 = features[5][1]
                # vol_R = features[4][2]
                neckline = {'slope': 0.0, 'intercept': 0.0}
                slope = (min2 - min1) / float(features[3][0] - features[1][0])
                neckline['slope'] = float(slope)
                intercept = min1 - slope * float(features[1][0])
                neckline['intercept'] = float(intercept)
                line = neckline['intercept'] + \
                    neckline['slope'] * float(features[5][0])

                if (features[5][1] > line) and (features[5][2] > vol_top):
                    # Head and shoulders -> bullish
                    detected['type'] = 'bullish'
                    detected['neckline'] = {'slope': 0.0, 'intercept': 0.0}
                    slope = (min2 - min1) / float(features[3][0] - features[1][0])
                    detected['neckline']['slope'] = slope
                    intercept = min1 - slope * float(features[1][0])

                    detected['neckline']['intercept'] = intercept
                    detected['indexes'] = features.copy()
                    detected['stats'] = {
                        'width': 0,
                        'avg': 0.0,
                        'stdev': 0.0,
                        'percent': 0.0
                    }
                    detected['stats']['width'] = features[4][0] - features[0][0]

                    feats = features.copy()
                    feats = [feat[1] for feat in feats]
                    detected['stats']['avg'] = np.round(np.mean(feats), 3)
                    detected['stats']['stdev'] = np.round(np.std(feats), 3)
                    detected['stats']['percent'] = np.round(
                        100.0 * np.std(feats) / np.mean(feats), 3)
    return detected


def feature_head_and_shoulders(fund: pd.DataFrame,
                               shapes: list,
                               filter_size: int = 10,
                               sanitize_dict=True) -> Tuple[dict, list, List[dict]]:
    """Feature Head and Shoulders

    Find head and shoulders feature of a reversal

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        shapes {list} -- list of shape objects

    Keyword Arguments:
        filter_size {int} -- period of exponential moving average filter
        sanitize_dict {bool} -- removes min/max lists so only feature-detected elements remain
                                (default: {True})
        name {str} -- (default: {''})

    Returns:
        Tuple[dict, list, List[dict]] -- dict of head shoulder features, moving average of fund,
            shapes
    """
    # Filter and find extrema. Reconstruct where those extremes exist on the actual signal.
    wma = windowed_moving_avg(fund, interval=filter_size)
    if filter_size == 0:
        extrema = find_filtered_local_extrema(wma, raw=True)
    else:
        extrema = find_filtered_local_extrema(wma)
    reconstructed_extrema = reconstruct_extrema(fund, extrema, filter_size, ma_type='windowed')

    # Cleanse data sample for duplicates and errors
    reconstructed_extrema = remove_duplicates(reconstructed_extrema)

    # Run detection algorithm (head and shoulders in this case)
    head_and_shoulders = find_head_shoulders(reconstructed_extrema, fund)

    # Cleanse data dictionary [again] and add dates for plotting features.
    head_and_shoulders = add_date_range(fund, head_and_shoulders, 5)
    head_and_shoulders = remove_empty_keys(head_and_shoulders)

    if sanitize_dict:
        head_and_shoulders.pop('max')
        head_and_shoulders.pop('min')

    if len(head_and_shoulders['features']) > 0:
        for feat in head_and_shoulders['features']:
            feature = {}
            feature['type'] = feat['type']
            feature['indexes'] = feat['indexes']
            shapes.append(feature)
    return head_and_shoulders, wma, shapes
