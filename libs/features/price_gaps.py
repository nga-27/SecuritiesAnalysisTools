""" Find Price Gaps """
import pandas as pd

from libs.tools import trends
from .feature_utils import feature_plotter

NEXT_STATE = {
    "breakaway": "runaway",
    "runaway": "exhaustion",
    "exhaustion": "breakaway"
}


def analyze_price_gaps(fund: pd.DataFrame, **kwargs) -> dict:
    """Analyze Price Gaps

    Determine state, if any, of price gaps for funds

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Optional Args:
        name {str} -- (default: {''})
        plot_output {bool} -- (default: {True})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- (default: {''})

    Returns:
        dict -- gaps data object
    """
    name = kwargs.get('name', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar = kwargs.get('progress_bar', None)
    view = kwargs.get('view', '')

    threshold = 0.0075
    gaps = get_gaps(fund, threshold=threshold)
    if progress_bar is not None:
        progress_bar.uptick(increment=0.25)

    gaps = determine_gap_types(fund, gaps)
    if progress_bar is not None:
        progress_bar.uptick(increment=0.25)

    feature_plotter(fund, shapes=gaps['plot'], name=name,
                    feature='price_gaps', plot_output=plot_output, view=view)
    if progress_bar is not None:
        progress_bar.uptick(increment=0.5)

    gaps['type'] = 'feature'

    return gaps


def get_gaps(fund: pd.DataFrame, threshold: float = 0.0) -> dict:
    """Get Gaps

    Arguments:
        fund {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        threshold {float} -- threshold for gaps (default: {0.0})

    Returns:
        dict -- dict of gap lists
    """
    gap_index = []
    gap_date = []
    gap_direction = []
    diff = []

    for i in range(1, len(fund['Close'])):

        if fund['High'][i-1] < fund['Low'][i] * (1.0 - threshold):
            # Positive price gap
            gap_index.append(i)
            gap_date.append(fund.index[i].strftime("%Y-%m-%d"))
            gap_direction.append("up")
            diff.append(fund['High'][i] - fund['High'][i-1])

        elif fund['High'][i] < fund['Low'][i-1] * (1.0 - threshold):
            # Negative price gap
            gap_index.append(i)
            gap_date.append(fund.index[i].strftime("%Y-%m-%d"))
            gap_direction.append("down")
            diff.append(fund['Low'][i] - fund['Low'][i-1])

    gaps = {
        "indexes": gap_index,
        "dates": gap_date,
        "direction": gap_direction,
        "difference": diff
    }
    return gaps


def determine_gap_types(fund: pd.DataFrame, gaps: dict) -> dict:
    """Determine Gap Types

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        gaps {dict} -- gap detection data object

    Keyword Arguments:
        name {str} -- (default: {''})

    Returns:
        dict -- gap data object
    """
    trend_short = trends.autotrend(fund['Close'], periods=[7], normalize=True)
    trend_med = trends.autotrend(fund['Close'], periods=[14], normalize=True)
    trend_long = trends.autotrend(fund['Close'], periods=[28], normalize=True)

    # TODO: Trends w/ gaps might provide insights...
    gaps['trend_short'] = []
    gaps['trend_med'] = []
    gaps['trend_long'] = []
    gaps['plot'] = []

    for i, index in enumerate(gaps['indexes']):
        gaps['trend_short'].append(trend_short[index])
        gaps['trend_med'].append(trend_med[index])
        gaps['trend_long'].append(trend_long[index])

        if gaps['direction'][i] == 'up':
            y_diff = float(gaps['difference'][i]) / 2.0 + fund['High'][index-1]
        else:
            y_diff = float(gaps['difference'][i]) / 2.0 + fund['Low'][index-1]

        gaps['plot'].append(
            {
                "type": gaps['direction'][i],
                "x": index,
                "y": y_diff,
                "rad": gaps['difference'][i]
            }
        )

    return gaps
