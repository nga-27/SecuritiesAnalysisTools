""" Trend of Periods """
import math
from typing import Tuple

import pandas as pd
import numpy as np
from scipy.stats import linregress

from .trend_utils import line_extender, line_reducer


def get_lines_from_period(fund: pd.DataFrame,
                          mins_and_maxes: list,
                          interval: int,
                          **kwargs) -> Tuple[list, list]:
    """Get Lines from Period

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        kargs {list} -- mins and maxes of x and y lists
        interval {int} -- period of time for a look back of a trend

    Optional Args:
        vf {dict} -- volatility quotient, used to determine if a trendline is still valid at the
                     end of the period by providing a volatility threshold (default: {0.06})

    Returns:
        Tuple[list,list] -- list of trendlines given the period (x, y)
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements,chained-comparison
    volatility = kwargs.get('vf', 0.06)
    extension = interval
    break_loop = 50
    cycles = int(np.floor(len(fund['Close']) / interval))
    mins_y = mins_and_maxes[1]
    mins_x = mins_and_maxes[0]
    maxes_y = mins_and_maxes[3]
    maxes_x = mins_and_maxes[2]
    set_of_x_lists = []
    set_of_y_lists = []

    for cycle in range(cycles):
        start = cycle * interval
        end = start + interval
        data = fund['Close'][start:end].copy()

        reg = linregress(x=list(range(start, end)), y=data)
        use_min = False
        if reg[0] >= 0:
            use_min = True

        count = 0
        st_count = count
        if use_min:
            while (count < len(mins_x)) and (mins_x[count] < start):
                count += 1
                st_count = count

            end_count = st_count
            while (count < len(mins_x)) and (mins_x[count] < end):
                count += 1
                end_count = count

            data_y = mins_y[st_count:end_count].copy()
            data_x = mins_x[st_count:end_count].copy()
            data_z = {}
            data_z['x'] = data_x
            data_z['y'] = data_y

            data_w = pd.DataFrame.from_dict(data_z)
            data_w.set_index('x')
            data_v = data_w.copy()

            stop_loop = 0
            while len(data_w['x']) > 0 and reg[0] > 0.0 and stop_loop < break_loop:
                reg = linregress(x=data_w['x'], y=data_w['y'])
                data_v = data_w.copy()
                data_w = data_w.loc[data_w['y'] < reg[0] * data_w['x'] + reg[1]]
                stop_loop += 1

            if reg[0] < 0.0:
                data_w = data_v.copy()
                if len(data_w) >= 2:
                    reg = linregress(x=data_w['x'], y=data_w['y'])

        else:
            while (count < len(maxes_x)) and (maxes_x[count] < start):
                count += 1
                st_count = count

            end_count = st_count
            while (count < len(maxes_x)) and (maxes_x[count] < end):
                count += 1
                end_count = count

            data_y = maxes_y[st_count:end_count].copy()
            data_x = maxes_x[st_count:end_count].copy()
            data_z = {}
            data_z['x'] = data_x
            data_z['y'] = data_y

            data_w = pd.DataFrame.from_dict(data_z)
            data_w.set_index('x')
            data_v = data_w.copy()

            stop_loop = 0
            while len(data_w['x']) > 0 and reg[0] < 0.0 and stop_loop < break_loop:
                reg = linregress(x=data_w['x'], y=data_w['y'])
                data_v = data_w.copy()
                data_w = data_w.loc[data_w['y'] > reg[0] * data_w['x'] + reg[1]]
                stop_loop += 1

            if reg[0] > 0.0:
                data_w = data_v.copy()
                if len(data_w) >= 2:
                    reg = linregress(x=data_w['x'], y=data_w['y'])

        end = line_extender(fund, list(range(start, end)), reg)
        if end != 0:
            max_range = [start, end]

            if max_range[1] > len(fund['Close']):
                max_range[1] = len(fund['Close'])
            if interval > 100:
                max_range[1] = len(fund['Close'])
            if end + extension > int(0.9 * float(len(fund['Close']))):
                max_range[1] = len(fund['Close'])

            max_range[1] = line_reducer(fund, max_range[1], reg, threshold=volatility)

            data_x = list(range(max_range[0], max_range[1]))
            data_y = [reg[0] * float(x) + reg[1] for x in data_x]

            if len(data_y) > 0 and not math.isnan(data_y[0]):
                set_of_x_lists.append(data_x)
                set_of_y_lists.append(data_y)

    return set_of_x_lists, set_of_y_lists
