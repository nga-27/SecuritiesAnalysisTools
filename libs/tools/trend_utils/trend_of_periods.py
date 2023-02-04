import math

import pandas as pd
import numpy as np
from scipy.stats import linregress

from .trend_utils import line_extender, line_reducer


def get_lines_from_period(fund: pd.DataFrame, kargs: list, interval: int, **kwargs) -> list:
    """Get Lines from Period

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        kargs {list} -- mins and maxes of x and y lists
        interval {int} -- period of time for a look back of a trend

    Optional Args:
        vf {dict} -- volatility quotient, used to determine if a trendline is still valid at the
                     end of the period by providing a volatility threshold (default: {0.06})

    Returns:
        list -- list of trendlines given the period
    """
    vf = kwargs.get('vf', 0.06)

    EXTENSION = interval
    BREAK_LOOP = 50
    cycles = int(np.floor(len(fund['Close'])/interval))
    mins_y = kargs[1]
    mins_x = kargs[0]
    maxes_y = kargs[3]
    maxes_x = kargs[2]
    X = []
    Y = []

    for cycle in range(cycles):
        start = cycle * interval
        end = start + interval
        data = fund['Close'][start:end].copy()

        x = list(range(start, end))
        reg = linregress(x=x, y=data)
        if reg[0] >= 0:
            use_min = True
        else:
            use_min = False

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

            datay = mins_y[st_count:end_count].copy()
            datax = mins_x[st_count:end_count].copy()
            dataz = {}
            dataz['x'] = datax
            dataz['y'] = datay
            dataw = pd.DataFrame.from_dict(dataz)
            dataw.set_index('x')
            datav = dataw.copy()

            stop_loop = 0
            while ((len(dataw['x']) > 0) and (reg[0] > 0.0)) and (stop_loop < BREAK_LOOP):
                reg = linregress(x=dataw['x'], y=dataw['y'])
                datav = dataw.copy()
                dataw = dataw.loc[dataw['y'] < reg[0] * dataw['x'] + reg[1]]
                stop_loop += 1

            if reg[0] < 0.0:
                dataw = datav.copy()
                if len(dataw) >= 2:
                    reg = linregress(x=dataw['x'], y=dataw['y'])

        else:
            while (count < len(maxes_x)) and (maxes_x[count] < start):
                count += 1
                st_count = count

            end_count = st_count
            while (count < len(maxes_x)) and (maxes_x[count] < end):
                count += 1
                end_count = count

            datay = maxes_y[st_count:end_count].copy()
            datax = maxes_x[st_count:end_count].copy()
            dataz = {}
            dataz['x'] = datax
            dataz['y'] = datay
            dataw = pd.DataFrame.from_dict(dataz)
            dataw.set_index('x')
            datav = dataw.copy()

            stop_loop = 0
            while ((len(dataw['x']) > 0) and (reg[0] < 0.0)) and (stop_loop < BREAK_LOOP):
                reg = linregress(x=dataw['x'], y=dataw['y'])
                datav = dataw.copy()
                dataw = dataw.loc[dataw['y'] > reg[0] * dataw['x'] + reg[1]]
                stop_loop += 1

            if reg[0] > 0.0:
                dataw = datav.copy()
                if len(dataw) >= 2:
                    reg = linregress(x=dataw['x'], y=dataw['y'])

        end = line_extender(fund, list(range(start, end)), reg)
        if end != 0:
            max_range = [start, end]

            if max_range[1] > len(fund['Close']):
                max_range[1] = len(fund['Close'])
            if interval > 100:
                max_range[1] = len(fund['Close'])
            if end + EXTENSION > int(0.9 * float(len(fund['Close']))):
                max_range[1] = len(fund['Close'])

            max_range[1] = line_reducer(
                fund, max_range[1], reg, threshold=vf)

            datax = list(range(max_range[0], max_range[1]))
            datay = [reg[0] * float(x) + reg[1] for x in datax]

            if (len(datay) > 0) and (not math.isnan(datay[0])):
                X.append(datax)
                Y.append(datay)

    return X, Y