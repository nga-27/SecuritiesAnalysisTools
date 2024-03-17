""" resistance support """
import os
from typing import Tuple, Union

import pandas as pd
import numpy as np

from libs.utils import generate_plot, PlotType, dates_convert_from_index, INDEXES

# pylint: disable=pointless-string-statement
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
    # pylint: disable=too-many-locals
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    time_frames = kwargs.get('timeframes', [13, 21, 34, 55])
    progress_bar = kwargs.get('progress_bar', None)
    view = kwargs.get('view', '')

    resist_support_lines = {}
    resist_support_lines['support'] = {}
    resist_support_lines['resistance'] = {}

    increment = 0.5 / (float(len(time_frames)))

    support = {}
    resistance = {}
    for time in time_frames:
        support[str(time)] = {}
        x_list, y_list = find_points(data, line_type='support',
                           time_frame=time, filter_type='windowed')
        support[str(time)]['x'] = x_list
        support[str(time)]['y'] = y_list
        sorted_support = sort_and_group(support)
        resist_support_lines['support'][str(time)] = cluster_notables(sorted_support, data)

        resistance[str(time)] = {}
        x2_list, y2_list = find_points(data, line_type='resistance', time_frame=time)
        resistance[str(time)]['x'] = x2_list
        resistance[str(time)]['y'] = y2_list
        sorted_resistance = sort_and_group(resistance)
        resist_support_lines['resistance'][str(
            time)] = cluster_notables(sorted_resistance, data)

        if progress_bar is not None:
            progress_bar.uptick(increment=increment)

    x_support, y_support, x_resistance, y_resistance = get_plot_content(
        data, resist_support_lines, selected_timeframe=str(time_frames[len(time_frames)-1]))

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    x_combined, y_combined = res_sup_unions(y_resistance, x_resistance, y_support, x_support)
    # Odd list behavior when no res/sup lines drawn on appends, so if-else to fix
    if len(y_combined) > 0:
        x_p = x_combined.copy()
        x_p2 = dates_convert_from_index(data, x_p)
        y_p = y_combined.copy()
        x_p2.append(data.index)
        y_p.append(remove_dates_from_close(data))
    else:
        x_p2 = data.index
        y_p = [remove_dates_from_close(data)]
    colors = colorize_plots(len(y_p), primary_plot_index=len(y_p)-1)

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    name2 = INDEXES.get(name, name)
    generate_plot(
        PlotType.GENERIC_PLOTTING, y_p, **{
            "x": x_p2, "colors": colors, "title": f'{name2} Major Resistance & Support',
            "save_fig": True,
            "plot_output": plot_output,
            "filename": os.path.join(name, view, f"resist_support_{name}.png")
        }
    )

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    analysis = detailed_analysis([y_resistance, y_support, y_combined],
        data, key_args={'Colors': colors})
    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    analysis['type'] = 'trend'

    return analysis


def truncate_points(x_list: list, y_list: list) -> Tuple[list, list]:
    """Truncate Points

    Shrink list of a resistance/support line so that it doesn't last the entire
    length of the data set (only the valid parts).

    Arguments:
        X {list} -- list of x values
        Y {list} -- list of y values

    Returns:
        list -- new, adjust lists of x and y values
    """
    new_x = []
    new_y = []
    for i, x_val in enumerate(x_list):
        if x_val not in new_x:
            new_x.append(x_val)
            new_y.append(y_list[i])
    return new_x, new_y


def find_points(data: pd.DataFrame, time_frame: int, **kwargs) -> Tuple[list, list]:
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
    x_list = []
    y_list = []

    if filter_type == 'windowed':
        sections = int(np.ceil(float(total_entries) / float(time_frame)))
        while sect_count < sections:
            left = sect_count * time_frame
            right = left + time_frame
            # print(f"tot: {total_entries}, left: {left}, right: {right}")
            if total_entries < (left + time_frame + 1):
                right = total_entries

            if line_type == 'support':
                val = np.min(data['Close'][left:right])
                point = np.where(data['Close'][left:right] == val)[0][0] + left
            else:
                val = np.max(data['Close'][left:right])
                point = np.where(data['Close'][left:right] == val)[0][0] + left

            x_list.append(point)
            y_list.append(val)

            sect_count += 1

    if filter_type == 'convolution':
        while sect_count + time_frame < total_entries:
            left = sect_count
            right = left + time_frame
            if total_entries < (left + time_frame + 1):
                right = total_entries

            if line_type == 'support':
                val = np.min(data['Close'][left:right])
                point = np.where(data['Close'][left:right] == val)[0][0] + left
            else:
                val = np.max(data['Close'][left:right])
                point = np.where(data['Close'][left:right] == val)[0][0] + left

            x_list.append(point)
            y_list.append(val)

            sect_count += 1
        x_list, y_list = truncate_points(x_list, y_list)

    return x_list, y_list


def sort_and_group(points: dict) -> list:
    """Sort and Group

    Group similar lines to avoid congestion

    Arguments:
        points {dict} -- points and lines to group

    Returns:
        list -- list of condensed lines
    """
    x_list = []
    y_list = []
    for key in points.keys():
        x_list.extend(points[key]['x'])
        y_list.extend(points[key]['y'])

    zipped = list(zip(x_list, y_list))
    zipped.sort(key=lambda x: x[1])
    notables = []
    t_note = 0
    for i in range(1, len(zipped)-1):
        val = (zipped[i][1] - zipped[i-1][1]) / zipped[i-1][1]
        val *= 100.0
        if -1 * CLUSTER_THRESHOLD < val < CLUSTER_THRESHOLD:
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
        if CLUSTER_THRESHOLD > val > -1 * CLUSTER_THRESHOLD:
            sub.append(sorted_x[i])
        else:
            clusters.append(sub)
            sub = []
            sub.append(sorted_x[i])

    lines = []
    for chunk in clusters:
        content = {}
        ys_list = []
        for x_val in chunk:
            ys_list.append(data['Close'][x_val])
        content['price'] = np.round(np.mean(ys_list), 2)
        content['x'] = chunk
        content['start'] = int(np.min(chunk))
        lines.append(content)

    return lines


def get_plot_content(data: pd.DataFrame,
                     rs_lines: dict,
                     selected_timeframe: str = '144') -> Tuple[list, list, list, list]:
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
    x_support = []
    y_support = []
    x_support.append(list(range(len(data['Close']))))
    y_support.append(data['Close'])

    x_resistance = []
    y_resistance = []
    x_resistance.append(list(range(len(data['Close']))))
    y_resistance.append(data['Close'])

    if 'support' in rs_lines.keys():
        if selected_timeframe in rs_lines['support'].keys():
            for key in rs_lines['support'][selected_timeframe]:
                x_list = list(range(key['start'], len(data['Close'])))
                y_list = [key['price']] * len(x_list)
                x_support.append(x_list)
                y_support.append(y_list)

    if 'resistance' in rs_lines.keys():
        if selected_timeframe in rs_lines['resistance'].keys():
            for key in rs_lines['resistance'][selected_timeframe]:
                x_list = list(range(key['start'], len(data['Close'])))
                y_list = [key['price']] * len(x_list)
                x_resistance.append(x_list)
                y_resistance.append(y_list)

    return x_support, y_support, x_resistance, y_resistance


def res_sup_unions(y_resistance: list, x_resistance: list,
                   y_support: list, x_support: list) -> Tuple[list, list]:
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
    # pylint: disable=too-many-locals
    y_combined = []
    x_combined = []

    y_combined.extend(y_resistance)
    x_combined.extend(x_resistance)
    y_combined.extend(y_support)
    x_combined.extend(x_support)

    combined = list(zip(x_combined, y_combined))
    combined.sort(key=lambda x: x[1][0])
    x_combined, y_combined = list(zip(*combined))

    no_changes = False
    while not no_changes:
        no_changes = True
        y_u = []
        x_u = []
        added_ith = False

        for i in range(1, len(y_combined)):
            neg = y_combined[i][0] * (1.0 - (MAJOR_GROUP_THRESHOLD / 100.0))
            pos = y_combined[i][0] * (1.0 + (MAJOR_GROUP_THRESHOLD / 100.0))

            if ((y_combined[i-1][0] > neg) and (y_combined[i-1][0] < pos)):
                # Two lines are near each other, average and combine. If added_ith=True, pop item
                # in list before to combine
                if added_ith:
                    added_ith = False
                    y_u.pop(len(y_u)-1)
                    x_u.pop(len(x_u)-1)

                start = min(x_combined[i-1][0], x_combined[i][0])
                end = max(
                    x_combined[i-1][len(x_combined[i-1])-1],
                    x_combined[i][len(x_combined[i])-1]
                )
                y_val = [np.round(np.mean([y_combined[i-1][0], y_combined[i][0]]), 2)] * (end-start)
                x_val = list(range(start, end))
                x_u.append(x_val)
                y_u.append(y_val)
                no_changes = False

            elif i == 1:
                # Special case where neither i=0 or i=1 are near, append both
                x_u.append(x_combined[i-1])
                x_u.append(x_combined[i])
                y_u.append(y_combined[i-1])
                y_u.append(y_combined[i])
                added_ith = True

            else:
                # ith case added
                x_u.append(x_combined[i])
                y_u.append(y_combined[i])
                added_ith = True

        y_val = [y[0] for y in y_u]

        x_combined = x_u.copy()
        y_combined = y_u.copy()

    return x_combined, y_combined


def get_nearest_lines(ylist: list,
                      cur_price: float,
                      support_resistance='support',
                      color: Union[list, None] = None) -> list:
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
    # pylint: disable=too-many-branches,too-many-statements
    if not color:
        color = []

    keys = []
    if support_resistance == 'major':
        for y_val in range(len(ylist)-1, -1, -1):
            percent = np.round((ylist[y_val] - cur_price) / cur_price * 100.0, 3)
            if percent < 0.0:
                state = 'Support'
            else:
                state = 'Resistance'

            y_color = 'black'
            if len(color) > 0:
                y_color = color[y_val]

            keys.append(
                {
                    'Price': f"{ylist[y_val]}",
                    'Change': f"{percent}%",
                    'Color': y_color,
                    'State': state
                })
        return keys

    if support_resistance == 'support':
        end_cap = 0
        count = 0
        modifier = -1
        while ((count < len(ylist)) and (cur_price > ylist[count])):
            count += 1
    else:
        end_cap = len(ylist) - 1
        count = len(ylist) - 1
        modifier = 1
        while ((count >= 0) and (cur_price < ylist[count])):
            count -= 1

    if count != end_cap:
        count += modifier
        if support_resistance == 'support':
            if (count - NUM_NEAREST_LINES) < 0:
                for i in range(count, -1, modifier):
                    percent = np.round(
                        (ylist[i] - cur_price) / cur_price * 100.0, 3)
                    if percent < 0.0:
                        state = 'Support'
                    else:
                        state = 'Resistance'
                    keys.append(
                        {'Price': f"{ylist[i]}", 'Change': f"{percent}%", 'State': state})

            else:
                for i in range(count, count - NUM_NEAREST_LINES, -1):
                    percent = np.round(
                        (ylist[i] - cur_price) / cur_price * 100.0, 3)
                    if percent < 0.0:
                        state = 'Support'
                    else:
                        state = 'Resistance'
                    keys.append(
                        {'Price': f"{ylist[i]}", 'Change': f"{percent}%", 'State': state})

        else:
            if (count + NUM_NEAREST_LINES) >= len(ylist) - 1:
                for i in range(count, len(ylist), modifier):
                    percent = np.round(
                        (ylist[i] - cur_price) / cur_price * 100.0, 3)
                    if percent < 0.0:
                        state = 'Support'
                    else:
                        state = 'Resistance'
                    keys.append(
                        {'Price': f"{ylist[i]}", 'Change': f"{percent}%", 'State': state})

            else:
                for i in range(count, count + NUM_NEAREST_LINES, modifier):
                    percent = np.round(
                        (ylist[i] - cur_price) / cur_price * 100.0, 3)
                    if percent < 0.0:
                        state = 'Support'
                    else:
                        state = 'Resistance'
                    keys.append(
                        {'Price': f"{ylist[i]}", 'Change': f"{percent}%", 'State': state})

    return keys


def detailed_analysis(zipped_content: list, data: pd.DataFrame,
                      key_args: Union[dict, None] = None) -> dict:
    """Detailed Analysis

    Arguments:
        zipped_content {list} -- x and y lists
        data {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        key_args {dict} -- key objects (default: {{}})

    Returns:
        dict -- resistance/support data object
    """
    if not key_args:
        key_args = {}

    analysis = {}
    colors = []

    for key in key_args.keys():
        analysis[key] = key_args[key]
    if 'Colors' in key_args.keys():
        colors = key_args['Colors']

    y_resistance = zipped_content[0]
    y_support = zipped_content[1]
    y_combined = zipped_content[2]

    res = [y[0] for y in y_resistance]
    sup = [y[0] for y in y_support]
    maj = [y[0] for y in y_combined]

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


def remove_dates_from_close(data_frame: pd.DataFrame) -> list:
    """Remove Dates from Close

    Cleanse data of dates in index

    Arguments:
        df {pd.DataFrame} -- fund dataset

    Returns:
        list -- fund dataset without dates
    """
    fixed_list = []
    for i in range(len(data_frame)):
        fixed_list.append(data_frame['Close'][i])
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
    num_colors = 6
    colors = []

    for i in range(len_of_plots):
        if i % num_colors == 1:
            colors.append('purple')
        elif i % num_colors == 2:
            colors.append('blue')
        elif i % num_colors == 3:
            colors.append('green')
        elif i % num_colors == 4:
            colors.append('yellow')
        elif i % num_colors == 5:
            colors.append('orange')
        elif i % num_colors == 0:
            colors.append('red')

    if primary_plot_index is not None:
        colors[primary_plot_index] = 'black'

    return colors
