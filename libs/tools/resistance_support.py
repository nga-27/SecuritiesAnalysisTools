import pandas as pd 
import numpy as np 

from libs.utils import generic_plotting

"""
    1. Combine points backward (i.e. for time=34 combine 34's and 21's)
    2. Sort on y
    3. Find clusters (< 1-2% change across group); continue only if multiple X's exist
    4. Find average Y of group, plot horizontal line from first X of group to end of plot
    4a. Alpha of color should be indicative of number in clusters
    ...
    5. Recall that Resistance = Support -> add functionality

"""
CLUSTER_THRESHOLD = 0.7

def find_points(data: pd.DataFrame, timeframe: int, line_type='support') -> list:
    total_entries = len(data['Close'])
    sections = int(np.ceil(float(total_entries) / float(timeframe)))
    sect_count = 0
    X = []
    Y = []

    while (sect_count < sections):
        left = sect_count * timeframe
        right = left + timeframe
        if total_entries < (left + timeframe + 1):
            right = total_entries

        if line_type == 'support':
            val = np.min(data['Close'][left:right])
            point = np.where(data['Close'][left:right] == val)[0][0] + left
        else:
            val = np.max(data['Close'][left:right])
            point = np.where(data['Close'][left:right] == val)[0][0] + left

        X.append(point)
        Y.append(val)
        
        sect_count += 1

    return X, Y


def sort_and_group(points: dict) -> list:
    x = []
    y = []
    for key in points.keys():
        x.extend(points[key]['x'])
        y.extend(points[key]['y'])
    zipped = list(zip(x, y))
    zipped.sort(key=lambda x: x[1])
    notables = []
    t_note = 0
    for i in range(1, len(zipped)-1):
        val = (zipped[i][1] - zipped[i-1][1]) / zipped[i-1][1]
        val *= 100.0
        if (val < CLUSTER_THRESHOLD) and (val > -1 * CLUSTER_THRESHOLD):
            if zipped[i-1][0] not in notables:
                notables.append(zipped[i-1][0])
                t_note += 1
            if zipped[i][0] not in notables:
                notables.append(zipped[i][0])
                t_note += 1
        else:
            if t_note < 2:
                if len(notables) != 0:
                    notables.pop(len(notables)-1)
            t_note = 0

    if t_note == 1:
        # Not reset to 0 but not 2+ either... case for last entry
        notables.pop(len(notables)-1)

    return notables


def cluster_notables(sorted_x: list, data: pd.DataFrame) -> list:
    clusters = []
    sub = []
    sub.append(sorted_x[0])
    for i in range(1, len(sorted_x)):
        val = (data['Close'][sorted_x[i]] - data['Close'][sub[len(sub)-1]]) / data['Close'][sub[len(sub)-1]] * 100.0
        if (val > -1*CLUSTER_THRESHOLD) and (val < CLUSTER_THRESHOLD):
            sub.append(sorted_x[i])
        else:
            clusters.append(sub)
            sub = []
            sub.append(sorted_x[i])
    lines = []
    for chunk in clusters:
        content = {}
        ys = []
        for x in chunk:
            ys.append(data['Close'][x])
        content['price'] = np.round(np.mean(ys), 2)
        content['x'] = chunk
        content['start'] = int(np.min(chunk))
        lines.append(content)
    return lines


def get_plot_content(data: pd.DataFrame, rs_lines: dict, selected_timeframe: str='144'):
    Xs = []
    Ys = []
    Xs.append(list(range(len(data['Close']))))
    Ys.append(data['Close'])

    Xr = []
    Yr = []
    Xr.append(list(range(len(data['Close']))))
    Yr.append(data['Close'])

    if 'support' in rs_lines.keys():
        if selected_timeframe in rs_lines['support'].keys():
            for key in rs_lines['support'][selected_timeframe]:
                x = list(range(key['start'], len(data['Close'])))
                y = [key['price']] * len(x)
                Xs.append(x)
                Ys.append(y)

    if 'resistance' in rs_lines.keys():
        if selected_timeframe in rs_lines['resistance'].keys():
            for key in rs_lines['resistance'][selected_timeframe]:
                x = list(range(key['start'], len(data['Close'])))
                y = [key['price']] * len(x)
                Xr.append(x)
                Yr.append(y)

    return Xs, Ys, Xr, Yr



def find_resistance_support_lines(data: pd.DataFrame, timeframes: list=[13, 21, 34, 55, 89, 144]):
    resist_support_lines = {}
    resist_support_lines['support'] = {}
    resist_support_lines['resistance'] = {}

    support = {}
    resistance = {}
    for time in timeframes:
        support[str(time)] = {}
        x, y = find_points(data, line_type='support', timeframe=time)
        support[str(time)]['x'] = x
        support[str(time)]['y'] = y
        sorted_support = sort_and_group(support)
        resist_support_lines['support'][str(time)] = cluster_notables(sorted_support, data)

        resistance[str(time)] = {}
        x2, y2 = find_points(data, line_type='resistance', timeframe=time)
        resistance[str(time)]['x'] = x2
        resistance[str(time)]['y'] = y2
        sorted_resistance = sort_and_group(resistance)
        resist_support_lines['resistance'][str(time)] = cluster_notables(sorted_resistance, data)

    Xs, Ys, Xr, Yr = get_plot_content(data, resist_support_lines, selected_timeframe=str(timeframes[len(timeframes)-1]))
    generic_plotting(Ys, x_=Xs, title='Support')
    generic_plotting(Yr, x_=Xr, title='Resistance')


