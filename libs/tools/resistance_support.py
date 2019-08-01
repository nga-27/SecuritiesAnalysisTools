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
NUM_NEAREST_LINES = 4

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


def res_sup_unions(Yr: list, Xr: list, Ys: list, Xs: list):
    Yc = []
    Xc = []
    for i, res in enumerate(Yr):
        for j, sup in enumerate(Ys):
            neg = sup[0] * (1.0 - (CLUSTER_THRESHOLD / 100.0))
            pos = sup[0] * (1.0 + (CLUSTER_THRESHOLD / 100.0))
            if (res[0] in sup) or ((res[0] > neg) and (res[0] < pos)):
                # Union X values...
                start_r = Xr[i][0]
                start_s = Xs[j][0]
                start = min(start_r, start_s)
                end = Xs[j][len(Xs[j])-1]
                x = list(range(start, end))
                Xc.append(x)
                y = [res[0]] * (end - start)
                Yc.append(y)

    return Xc, Yc


def get_nearest_lines(ylist: list, cur_price: float, support_resistance='support') -> list:
    keys = []
    if support_resistance == 'major':
        for y in range(len(ylist)-1, -1, -1):
            percent = np.round((ylist[y] - cur_price) / cur_price * 100.0, 3)
            keys.append({'Price': f"{ylist[y]}", 'Change': f"{percent}%"})
        return keys

    elif support_resistance == 'support':
        endcap = 0
        count = 0
        modifier = -1
        while ((count < len(ylist)) and (cur_price > ylist[count])):
            count += 1
    else:
        endcap = len(ylist) - 1
        count = len(ylist) - 1
        modifier = 1
        while ((count >= 0) and (cur_price < ylist[count])):
            count -= 1
    if count != endcap:
        count += modifier
        if support_resistance == 'support':
            if (count - NUM_NEAREST_LINES) < 0:
                for i in range(count, -1, modifier):
                    percent = np.round((ylist[i] - cur_price) / cur_price * 100.0, 3)
                    keys.append({'Price': f"{ylist[i]}", 'Change': f"{percent}%"})
            else: 
                for i in range(count, count - NUM_NEAREST_LINES, -1):
                    percent = np.round((ylist[i] - cur_price) / cur_price * 100.0, 3)
                    keys.append({'Price': f"{ylist[i]}", 'Change': f"{percent}%"})
        else:
            if (count + NUM_NEAREST_LINES) >= len(ylist) - 1:
                for i in range(count, len(ylist), modifier):
                    percent = np.round((ylist[i] - cur_price) / cur_price * 100.0, 3)
                    keys.append({'Price': f"{ylist[i]}", 'Change': f"{percent}%"})
            else: 
                for i in range(count, count + NUM_NEAREST_LINES, modifier):
                    percent = np.round((ylist[i] - cur_price) / cur_price * 100.0, 3)
                    keys.append({'Price': f"{ylist[i]}", 'Change': f"{percent}%"})
    return keys



def detailed_analysis(zipped_content: list, data: pd.DataFrame) -> dict:
    analysis = {}
    Yr = zipped_content[0]
    Ys = zipped_content[1]
    Yc = zipped_content[2]
    res = [y[0] for y in Yr]
    sup = [y[0] for y in Ys]
    maj = [y[0] for y in Yc]
    res.sort()
    sup.sort()
    maj.sort()

    analysis['current price'] = data['Close'][len(data['Close'])-1]
    analysis['supports'] = get_nearest_lines(sup, analysis['current price'], support_resistance='support')
    analysis['resistances'] = get_nearest_lines(res, analysis['current price'], support_resistance='resistance')
    analysis['major S&R'] = get_nearest_lines(maj, analysis['current price'], support_resistance='major')
    
    return analysis


def find_resistance_support_lines(  data: pd.DataFrame, 
                                    plot_output: bool=False,
                                    name: str='',
                                    timeframes: list=[13, 21, 34, 55, 89, 144]) -> dict:
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
    generic_plotting(Ys, x_=Xs, title=f'{name} Support')
    generic_plotting(Yr, x_=Xr, title=f'{name} Resistance')

    Xc, Yc = res_sup_unions(Yr, Xr, Ys, Xs)
    Xc.append(list(range(len(data['Close']))))
    Yc.append(data['Close'])
    generic_plotting(Yc, x_=Xc, title=f'{name} Major Resistance & Support')

    analysis = detailed_analysis([Yr, Ys, Yc], data)
    print(analysis)
    return analysis

