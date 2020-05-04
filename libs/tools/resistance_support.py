import os
import pandas as pd
import numpy as np

from libs.utils import generic_plotting, dates_convert_from_index
from libs.utils import ProgressBar, SP500

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
MAJOR_GROUP_THRESHOLD = 1.1
NUM_NEAREST_LINES = 7


def find_resistance_support_lines(data: pd.DataFrame, **kwargs) -> dict:
    """Find Resistance / Support Lines

    Arguments:
        data {pd.DataFrame} -- fund historical data

    Optional Args:
        name {str} -- name of fund, primarily for plotting (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        timeframes {list} -- time windows for feature discovery (default: {[13, 21, 34, 55]})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- directory of plots (default: {''})

    Returns:
        dict -- contains all trendline information
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    timeframes = kwargs.get('timeframes', [13, 21, 34, 55])
    progress_bar = kwargs.get('progress_bar', None)
    view = kwargs.get('view', '')

    resist_support_lines = {}
    resist_support_lines['support'] = {}
    resist_support_lines['resistance'] = {}

    increment = 0.5 / (float(len(timeframes)))

    support = {}
    resistance = {}
    for time in timeframes:
        support[str(time)] = {}
        x, y = find_points(data, line_type='support',
                           timeframe=time, filter_type='windowed')
        support[str(time)]['x'] = x
        support[str(time)]['y'] = y
        sorted_support = sort_and_group(support)
        resist_support_lines['support'][str(
            time)] = cluster_notables(sorted_support, data)

        resistance[str(time)] = {}
        x2, y2 = find_points(data, line_type='resistance', timeframe=time)
        resistance[str(time)]['x'] = x2
        resistance[str(time)]['y'] = y2
        sorted_resistance = sort_and_group(resistance)
        resist_support_lines['resistance'][str(
            time)] = cluster_notables(sorted_resistance, data)

        if progress_bar is not None:
            progress_bar.uptick(increment=increment)

    Xs, Ys, Xr, Yr = get_plot_content(
        data, resist_support_lines, selected_timeframe=str(timeframes[len(timeframes)-1]))

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    Xc, Yc = res_sup_unions(Yr, Xr, Ys, Xs)
    # Odd list behavior when no res/sup lines drawn on appends, so if-else to fix
    if len(Yc) > 0:
        Xp = Xc.copy()
        Xp2 = dates_convert_from_index(data, Xp)
        Yp = Yc.copy()
        Xp2.append(data.index)
        Yp.append(remove_dates_from_close(data))
    else:
        Xp2 = data.index
        Yp = [remove_dates_from_close(data)]
    c = colorize_plots(len(Yp), primary_plot_index=len(Yp)-1)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    name2 = SP500.get(name, name)
    if plot_output:
        generic_plotting(Yp, x=Xp2, colors=c,
                         title=f'{name2} Major Resistance & Support')
    else:
        filename = f"{name}/{view}/resist_support_{name}.png"
        generic_plotting(
            Yp, x=Xp2, colors=c, title=f'{name2} Major Resistance & Support', saveFig=True, filename=filename)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    analysis = detailed_analysis([Yr, Ys, Yc], data, key_args={'Colors': c})
    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    analysis['type'] = 'trend'

    return analysis


def truncate_points(X: list, Y: list) -> list:
    """Truncate Points

    Shrink list of a resistance/support line so that it doesn't last the entire
    length of the data set (only the valid parts).

    Arguments:
        X {list} -- list of x values
        Y {list} -- list of y values

    Returns:
        list -- new, adjust lists of x and y values
    """
    new_X = []
    new_Y = []
    for i, x in enumerate(X):
        if x not in new_X:
            new_X.append(x)
            new_Y.append(Y[i])
    return new_X, new_Y


def find_points(data: pd.DataFrame, timeframe: int, **kwargs) -> list:
    """Find Points

    Arguments:
        data {pd.DataFrame} 
        timeframe {int} -- time window (number of periods)

    Keyword Arguments:
        line_type {str} -- (default: {'support'})
        filter_type {str} -- signal filter (default: {'windowed'})

    Returns:
        list -- list of points
    """
    line_type = kwargs.get('line_type', 'support')
    filter_type = kwargs.get('filter_type', 'windowed')

    total_entries = len(data['Close'])
    if pd.isna(data['Close'][total_entries-1]):
        total_entries -= 1

    sect_count = 0
    X = []
    Y = []

    if filter_type == 'windowed':
        sections = int(np.ceil(float(total_entries) / float(timeframe)))
        while (sect_count < sections):
            left = sect_count * timeframe
            right = left + timeframe
            # print(f"tot: {total_entries}, left: {left}, right: {right}")
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

    if filter_type == 'convolution':
        while (sect_count + timeframe < total_entries):
            left = sect_count
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
        X, Y = truncate_points(X, Y)

    return X, Y


def sort_and_group(points: dict) -> list:
    """Sort and Group

    Group similar lines to avoid congestion

    Arguments:
        points {dict} -- points and lines to group

    Returns:
        list -- list of condensed lines
    """
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
    """Cluster Notables

    Continued grouping of similar signals

    Arguments:
        sorted_x {list} -- x list of sorted content
        data {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of clustered lines
    """
    clusters = []
    sub = []
    if len(sorted_x) == 0:
        return []

    sub.append(sorted_x[0])
    for i in range(1, len(sorted_x)):
        val = (data['Close'][sorted_x[i]] - data['Close']
               [sub[len(sub)-1]]) / data['Close'][sub[len(sub)-1]] * 100.0
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


def get_plot_content(data: pd.DataFrame,
                     rs_lines: dict,
                     selected_timeframe: str = '144') -> list:
    """Get Plot Content

    Generate plot lists for resistance/support lines

    Arguments:
        data {pd.DataFrame} -- fund dataset
        rs_lines {dict} -- resistance support data object

    Keyword Arguments:
        selected_timeframe {str} -- timeframe (default: {'144'})

    Returns:
        list -- x-support, y-support, x-resistance, y-resistance lists
    """
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


def res_sup_unions(Yr: list, Xr: list, Ys: list, Xs: list) -> list:
    """Resistance / Support Unions

    Join a resistance/support line that becomes a support/resistance line. Combines Resistances and
    Supports within the MAJOR_GROUP_THRESHOLD window.

    Arguments:
        Yr {list} -- y-resistance points
        Xr {list} -- x-resistance points
        Ys {list} -- y-support points
        Xs {list} -- x-support points

    Returns:
        list -- x-combined points, y-combined points lists
    """
    Yc = []
    Xc = []

    Yc.extend(Yr)
    Xc.extend(Xr)
    Yc.extend(Ys)
    Xc.extend(Xs)

    C = list(zip(Xc, Yc))
    C.sort(key=lambda x: x[1][0])
    Xc, Yc = list(zip(*C))

    no_changes = False
    while not no_changes:
        no_changes = True
        Yu = []
        Xu = []
        added_ith = False

        for i in range(1, len(Yc)):
            neg = Yc[i][0] * (1.0 - (MAJOR_GROUP_THRESHOLD / 100.0))
            pos = Yc[i][0] * (1.0 + (MAJOR_GROUP_THRESHOLD / 100.0))

            if ((Yc[i-1][0] > neg) and (Yc[i-1][0] < pos)):
                # Two lines are near each other, average and combine. If added_ith=True, pop item
                # in list before to combine
                if added_ith:
                    added_ith = False
                    Yu.pop(len(Yu)-1)
                    Xu.pop(len(Xu)-1)
                start = min(Xc[i-1][0], Xc[i][0])
                end = max(Xc[i-1][len(Xc[i-1])-1], Xc[i][len(Xc[i])-1])
                y = [np.round(np.mean([Yc[i-1][0], Yc[i][0]]), 2)
                     ] * (end-start)
                x = list(range(start, end))
                Xu.append(x)
                Yu.append(y)
                no_changes = False

            elif (i == 1):
                # Special case where neither i=0 or i=1 are near, append both
                Xu.append(Xc[i-1])
                Xu.append(Xc[i])
                Yu.append(Yc[i-1])
                Yu.append(Yc[i])
                added_ith = True

            else:
                # ith case added
                Xu.append(Xc[i])
                Yu.append(Yc[i])
                added_ith = True

        y = [y[0] for y in Yu]

        Xc = Xu.copy()
        Yc = Yu.copy()

    return Xc, Yc


def get_nearest_lines(ylist: list,
                      cur_price: float,
                      support_resistance='support',
                      color=[]) -> list:
    """Get Nearest Lines

    Arguments:
        ylist {list} -- list of prices and lines near current price
        cur_price {float}

    Keyword Arguments:
        support_resistance {str} -- control key (+/-) (default: {'support'})
        color {list} -- list of colors to plot (default: {[]})

    Returns:
        list -- keys, list of price-to-list objects
    """
    keys = []
    if support_resistance == 'major':
        for y in range(len(ylist)-1, -1, -1):
            percent = np.round((ylist[y] - cur_price) / cur_price * 100.0, 3)
            y_color = 'black'
            if len(color) > 0:
                y_color = color[y]
            keys.append(
                {'Price': f"{ylist[y]}", 'Change': f"{percent}%", 'Color': y_color})
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
                    percent = np.round(
                        (ylist[i] - cur_price) / cur_price * 100.0, 3)
                    keys.append(
                        {'Price': f"{ylist[i]}", 'Change': f"{percent}%"})

            else:
                for i in range(count, count - NUM_NEAREST_LINES, -1):
                    percent = np.round(
                        (ylist[i] - cur_price) / cur_price * 100.0, 3)
                    keys.append(
                        {'Price': f"{ylist[i]}", 'Change': f"{percent}%"})

        else:
            if (count + NUM_NEAREST_LINES) >= len(ylist) - 1:
                for i in range(count, len(ylist), modifier):
                    percent = np.round(
                        (ylist[i] - cur_price) / cur_price * 100.0, 3)
                    keys.append(
                        {'Price': f"{ylist[i]}", 'Change': f"{percent}%"})

            else:
                for i in range(count, count + NUM_NEAREST_LINES, modifier):
                    percent = np.round(
                        (ylist[i] - cur_price) / cur_price * 100.0, 3)
                    keys.append(
                        {'Price': f"{ylist[i]}", 'Change': f"{percent}%"})

    return keys


def detailed_analysis(zipped_content: list, data: pd.DataFrame, key_args={}) -> dict:
    """Detailed Analysis

    Arguments:
        zipped_content {list} -- x and y lists
        data {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        key_args {dict} -- key objects (default: {{}})

    Returns:
        dict -- resistance/support data object
    """
    analysis = {}
    colors = []

    for key in key_args.keys():
        analysis[key] = key_args[key]
    if 'Colors' in key_args.keys():
        colors = key_args['Colors']

    Yr = zipped_content[0]
    Ys = zipped_content[1]
    Yc = zipped_content[2]

    res = [y[0] for y in Yr]
    sup = [y[0] for y in Ys]
    maj = [y[0] for y in Yc]

    zipper = list(zip(maj, colors))
    zipper.sort(key=lambda x: x[0])
    maj = [x[0] for x in zipper]
    colors = [y[1] for y in zipper]

    res.sort()
    sup.sort()
    maj.sort()

    # Mutual funds tickers update daily, several hours after close. To accomodate for any pulls of
    # data at any time, we must know that the last [current] index may not be 'None' / 'nan'. Update
    # length of plotting to accomodate.
    analysis['current price'] = data['Close'][len(data['Close'])-1]
    if pd.isna(analysis['current price']):
        analysis['current price'] = data['Close'][len(data['Close'])-2]

    analysis['supports'] = get_nearest_lines(
        maj, analysis['current price'], support_resistance='support')
    analysis['resistances'] = get_nearest_lines(
        maj, analysis['current price'], support_resistance='resistance')
    analysis['major S&R'] = get_nearest_lines(
        maj, analysis['current price'], support_resistance='major', color=colors)

    return analysis


def remove_dates_from_close(df: pd.DataFrame) -> list:
    """Remove Dates from Close

    Cleanse data of dates in index

    Arguments:
        df {pd.DataFrame} -- fund dataset

    Returns:
        list -- fund dataset without dates
    """
    fixed_list = []
    for i in range(len(df)):
        fixed_list.append(df['Close'][i])
    return fixed_list


def colorize_plots(len_of_plots: int, primary_plot_index: int = None) -> list:
    """Colorize Plots

    Arguments:
        len_of_plots {int}

    Keyword Arguments:
        primary_plot_index {int} -- used for plotting price itself (default: {None})

    Returns:
        list -- list of colors
    """
    NUM_COLORS = 6
    colors = []

    for i in range(len_of_plots):
        if i % NUM_COLORS == 1:
            colors.append('purple')
        elif i % NUM_COLORS == 2:
            colors.append('blue')
        elif i % NUM_COLORS == 3:
            colors.append('green')
        elif i % NUM_COLORS == 4:
            colors.append('yellow')
        elif i % NUM_COLORS == 5:
            colors.append('orange')
        elif i % NUM_COLORS == 0:
            colors.append('red')

    if primary_plot_index is not None:
        colors[primary_plot_index] = 'black'

    return colors
