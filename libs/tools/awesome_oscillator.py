import pandas as pd
import numpy as np

from libs.utils import ProgressBar
from .moving_average import simple_moving_avg


def awesome_oscillator(position: pd.DataFrame, **kwargs) -> dict:
    """
    Relative Strength Indicator

    args:
        position:       (pd.DataFrame) list of y-value datasets to be plotted (multiple)

    optional args:
        name:           (list) name of fund, primarily for plotting; DEFAULT=''
        plot_output:    (bool) True to render plot in realtime; DEFAULT=True
        period:         (int) size of RSI indicator; DEFAULT=14 
        out_suppress:   (bool) output plot/prints are suppressed; DEFAULT=True
        progress_bar:   (ProgressBar) DEFAULT=None
        overbought:     (float) threshold to trigger overbought/sell condition; DEFAULT=70.0
        oversold:       (float) threshold to trigger oversold/buy condition; DEFAULT=30.0
        auto_trend:     (bool) True calculates basic trend, applies to thresholds; DEFAULT=True

    returns:
        rsi_swings:     (dict) contains all rsi information
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar = kwargs.get('progress_bar')

    ao = dict()

    signal = get_ao_signal(position, plot_output=plot_output,
                           name=name, progress_bar=progress_bar)

    if progress_bar is not None:
        progress_bar.uptick(increment=1.0)
    return ao


def get_ao_signal(position: pd.DataFrame, **kwargs) -> list:

    short_period = kwargs.get('short_period', 5)
    long_period = kwargs.get('long_period', 34)
    filter_style = kwargs.get('filter_style', 'sma')
    plot_output = kwargs.get('plot_output', True)
    p_bar = kwargs.get('progress_bar')
    name = kwargs.get('name', '')

    signal = []

    return signal
