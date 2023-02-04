""" Line Utilities """
from typing import Tuple

import numpy as np


def consolidate_lines(line_content: list,
                      lines: list,
                      x_lines: list,
                      signal: list,
                      **kwargs) -> Tuple[list, list, list]:
    """Consolidate Lines

    Arguments:
        line_content {list} -- list of trendline objects
        lines {list} -- list of trendlines
        x_lines {list} -- list of x-values of trendlines
        signal {list} -- signal of trendlines

    Optional Args:
        thresh {float} -- percent for angle combination (default: {2.5})

    Returns:
        list -- modified line content, modified lines, modified x lines
    """
    # pylint: disable=too-many-locals
    thresh = kwargs.get('thresh', 2.5)
    thresh2 = thresh / 20.0

    nan_free = []
    for sortie in line_content:
        if str(sortie['slope']) != 'nan':
            nan_free.append(sortie)

    sort_by_slope = sorted(nan_free, key=lambda x: x['angle'])

    kept_grouped = []
    count_base = 0
    count_comp = 1
    kept_local = [sort_by_slope[count_base]['id']]

    while count_base < len(sort_by_slope) and count_comp < len(sort_by_slope):

        base_upper = thresh + sort_by_slope[count_base]['angle']
        comp_lower = sort_by_slope[count_comp]['angle']

        if base_upper > comp_lower:

            if sort_by_slope[count_base]['intercept'] < 0.0:
                base_lower = (1.0 - thresh2) * \
                    sort_by_slope[count_base]['intercept']
                comp_upper = (1.0 + thresh2) * \
                    sort_by_slope[count_comp]['intercept']

                if base_lower > comp_upper:  # or base_lower < comp_upper:
                    kept_local.append(sort_by_slope[count_comp]['id'])
                    count_comp += 1
                    continue

            else:
                base_upper = (1.0 + thresh2) * \
                    sort_by_slope[count_base]['intercept']
                comp_lower = (1.0 - thresh2) * \
                    sort_by_slope[count_comp]['intercept']

                if base_upper > comp_lower:  # or base_lower < comp_upper:
                    kept_local.append(sort_by_slope[count_comp]['id'])
                    count_comp += 1
                    continue

        count_base = count_comp
        count_comp += 1
        kept_grouped.append(kept_local.copy())
        kept_local = [sort_by_slope[count_base]['id']]

    new_content, lines, x_lines = reconstruct_lines(kept_grouped, line_content, x_lines, signal)
    return new_content, lines, x_lines


def reconstruct_lines(groups: list,
                      content: list,
                      x_s: list,
                      signal: list) -> Tuple[list, list, list]:
    """Reconstruct Lines

    Join similar lines

    Arguments:
        groups {list} -- list of IDs
        content {list} -- content of lines
        lines {list} -- trendlines
        x_s {list} -- x's of trendlines
        signal {list} -- signal of which trendlines are generated

    Returns:
        list -- new content, new lines, new x lists
    """
    # pylint: disable=too-many-locals
    new_lines = []
    new_xs = []
    new_content = []
    new_id = 0

    y_max = max(signal) - min(signal)
    x_max = len(signal)
    scale_change = x_max / y_max

    for id_list in groups:
        slope = []
        intercept = []
        start = []
        end = []

        for id_ in id_list:
            slope.append(content[id_]['slope'])
            intercept.append(content[id_]['intercept'])
            start.append(x_s[id_][0])
            end.append(x_s[id_][-1])

        slope = np.mean(slope)
        intercept = np.mean(intercept)
        item = {'slope': slope, 'intercept': intercept}
        item['angle'] = np.arctan(slope * scale_change) / np.pi * 180.0
        if slope < 0.0:
            item['angle'] = 180.0 + \
                (np.arctan(slope * scale_change) / np.pi * 180.0)

        start = np.min(start)
        end = np.max(end)

        xs_val = list(range(start, end+1))
        line = [slope * x + intercept for x in xs_val]
        line, xs_val = filter_nearest_to_signal(signal, xs_val, line, threshold=0.03, ratio=True)

        if len(xs_val) > 4:
            item['length'] = len(line)
            item['id'] = new_id
            new_content.append(item)
            new_id += 1

            new_lines.append(line)
            new_xs.append(xs_val)

    return new_content, new_lines, new_xs


def filter_nearest_to_signal(signal: list,
                             x_line: list,
                             line: list,
                             threshold=0.05,
                             ratio=False) -> list:
    """Filter Nearest to Signal

    Arguments:
        signal {list} -- signal to find trendlines
        x_line {list} -- list of xs corresponding to lines
        line {list} -- trendline y-values

    Keyword Arguments:
        threshold {float} -- percent within signal (default: {0.05})
        ratio {bool} -- adjustments of x values (default: {False})

    Returns:
        list -- corrected lines, corrected xs
    """
    removals = []
    for j, lin in enumerate(line):
        if lin < 0.0:
            if lin < ((1.0 + threshold) * signal[x_line[j]]) or \
                    lin > ((1.0 - threshold) * signal[x_line[j]]):
                removals.append(j)
        else:
            if lin > ((1.0 + threshold) * signal[x_line[j]]) or \
                    lin < ((1.0 - threshold) * signal[x_line[j]]):
                removals.append(j)

    line_corrected = []
    x_corrected = []
    indexes = []
    for j, x_val in enumerate(x_line):
        if j not in removals:
            x_corrected.append(x_val)
            indexes.append(j)

    if len(x_corrected) > 0:
        start = min(x_corrected)
        end = max(x_corrected)
        x_corrected = list(range(start, end+1))

        if ratio:
            start = min(indexes)
            end = max(indexes)

        line_corrected = line[start:end+1].copy()

    return line_corrected, x_corrected
