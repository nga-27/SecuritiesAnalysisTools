import pandas as pd 
import numpy as np 

from libs.utils import ProgressBar

def analyze_price_gaps(fund: pd.DataFrame, **kwargs) -> dict:
    """
    Analyze Price Gaps - determine state, if any, of price gaps for funds

    args:
        position:       (pd.DataFrame) list of y-value datasets to be plotted (multiple)

    optional args:
        name:           (list) name of fund, primarily for plotting; DEFAULT=''
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        progress_bar:   (ProgressBar) DEFAULT=None
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar = kwargs.get('progress_bar', None)

    gaps = {}

    return gaps