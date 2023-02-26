""" Moving Average Utils """
from typing import Tuple

import pandas as pd
import numpy as np


def find_crossovers(mov_avg: dict, position: pd.DataFrame) -> list:
    """Find Crossovers

    Find crossovers in signals, particularly with a short/medium/long average

    Arguments:
        mov_avg {dict} -- triple moving average data object
        position {pd.DataFrame} -- fund dataset

    Returns:
        list -- list of crossover event dictionaries
    """
    # pylint: disable=too-many-branches
    t_short = mov_avg['tabular']["short"]
    t_med = mov_avg['tabular']["medium"]
    t_long = mov_avg['tabular']["long"]

    sh_period = mov_avg['short']['period']
    md_period = mov_avg['medium']['period']
    ln_period = mov_avg['long']['period']

    features = []
    if any([len(t_short) == 0, len(t_med) == 0, len(t_long) == 0]):
        return features

    state = 'at'
    for i, short in enumerate(t_short):
        data = None
        date = position.index[i].strftime("%Y-%m-%d")

        if state == 'at':
            if short > t_med[i]:
                state = 'above'
                data = {
                    "type": 'bullish',
                    "value": f'golden crossover (midterm: {sh_period}d > {md_period}d)',
                    "index": i,
                    "date": date
                }
            elif short < t_med[i]:
                state = 'below'
                data = {
                    "type": 'bearish',
                    "value": f'death crossover (midterm: {md_period}d > {sh_period}d)',
                    "index": i,
                    "date": date
                }

        elif state == 'above':
            if short < t_med[i]:
                state = 'below'
                data = {
                    "type": 'bearish',
                    "value": f'death crossover (midterm: {md_period}d > {sh_period}d)',
                    "index": i,
                    "date": date
                }

        elif state == 'below':
            if short > t_med[i]:
                state = 'above'
                data = {
                    "type": 'bullish',
                    "value": f'golden crossover (midterm: {sh_period}d > {md_period}d)',
                    "index": i,
                    "date": date
                }

        if data is not None:
            features.append(data)

    state = 'at'
    for i, med in enumerate(t_med):
        data = None
        date = position.index[i].strftime("%Y-%m-%d")

        if state == 'at':
            if med > t_long[i]:
                state = 'above'
                data = {
                    "type": 'bullish',
                    "value": f'golden crossover (longterm: {md_period}d > {ln_period}d)',
                    "index": i,
                    "date": date
                }
            elif med < t_long[i]:
                state = 'below'
                data = {
                    "type": 'bearish',
                    "value": f'death crossover (longterm: {ln_period}d > {md_period}d)',
                    "index": i,
                    "date": date
                }

        elif state == 'above':
            if med < t_long[i]:
                state = 'below'
                data = {
                    "type": 'bearish',
                    "value": f'death crossover (longterm: {ln_period}d > {md_period}d)',
                    "index": i,
                    "date": date
                }

        elif state == 'below':
            if med > t_long[i]:
                state = 'above'
                data = {
                    "type": 'bullish',
                    "value": f'golden crossover (longterm: {md_period}d > {ln_period}d)',
                    "index": i,
                    "date": date
                }

        if data is not None:
            features.append(data)
    return features


def adjust_signals(fund: pd.DataFrame, signal: list, offset: int = 0) -> Tuple[list, list]:
    """Adjust Signals

    Arguments:
        fund {pd.DataFrame} -- fund dataset (with index as dates)
        signal {list} -- signal to adjust

    Keyword Arguments:
        offset {int} -- starting point (default: {0})

    Returns:
        list -- new adjusted x_plots, adjusted signal
    """
    x_values = []
    adj_signal = []
    for i in range(offset, len(signal)):
        x_values.append(fund.index[i])
        adj_signal.append(signal[i])
    return x_values, adj_signal


def normalize_signals_local(signals: list) -> list:
    """ Normalize local signals based off max """
    max_ = 0.0
    for sig in signals:
        m_val = np.max(np.abs(sig))
        if m_val > max_:
            max_ = m_val

    if max_ != 0.0:
        for _, sig in enumerate(signals):
            new_sig = []
            for point in sig:
                pt2 = point / max_
                new_sig.append(pt2)
            sig = new_sig.copy()

    return signals
