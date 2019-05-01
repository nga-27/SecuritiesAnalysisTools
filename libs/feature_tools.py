import pandas as pd 
import numpy as np 

from .features import find_head_shoulders
from .features import local_extrema, reconstruct_extrema, remove_duplicates, add_daterange, remove_empty_keys, plotter
from .moving_average import exponential_ma


def feature_head_and_shoulders(fund: pd.DataFrame, FILTER_SIZE=10, sanitize_dict=True):
    """ 
    Find head and shoulders feature of a reversal 
    Args:
        fund - pd.DataFrame of fund over a period
        FILTER_SIZE - (int) period of ema filter
    Returns:
        hs - dict of head and shoulders features
        ma - (list) fund filtered with ema
    """

    ma = exponential_ma(fund, FILTER_SIZE)
    ex = local_extrema(ma)
    r = reconstruct_extrema(fund['Close'], ex, FILTER_SIZE)
    r = remove_duplicates(r)
    hs = find_head_shoulders(r) 
    hs = add_daterange(fund, hs, 5)
    hs = remove_empty_keys(hs) 
    
    if sanitize_dict:
        hs.pop('max')
        hs.pop('min')
    
    return hs, ma

