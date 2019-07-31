import pandas as pd 
import numpy as np 

from libs.utils import generic_plotting

"""
    1. Combine points backward (i.e. for time=34 combine 34's and 21's)
    2. Sort on y
    3. Find clusters (< 1-2% change across group); continue only if multiple X's exist
    4. Find average Y of group, plot horizontal line from first X of group to end of plot
    4a. Alpha of color should be indicative of number in clusters

"""

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


def percent_slopes(y: list) -> list:
    slopes = []
    slopes.append(0)
    for i in range(1, len(y)):
        val = (y[i] - y[i-1]) / y[i-1] * 100.0
        slopes.append(val)
    return slopes

def sort_and_group(x: list, y: list):
    zipped = list(zip(x, y))
    zipped.sort(key=lambda x: x[1])
    print(zipped[0][1])


def find_resistance_support_lines(data: pd.DataFrame, timeframes: list=[21, 34, 55, 89, 144]):
    X = []
    Y = []
    slope = []
    for time in timeframes:
        x, y = find_points(data, line_type='support', timeframe=time)
        X.append(x)
        Y.append(y)
        slope.append(percent_slopes(y))
        sort_and_group(x, y)
    X.append(list(range(len(data['Close']))))
    Y.append(data['Close'])
    generic_plotting(Y, x_=X, title='Support Vectors')
    generic_plotting(slope, x_=X, title='Support Slopes')

