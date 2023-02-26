"""
#   Technical Analysis Tools
#
#   by: nga-27
#
#   A program that outputs a graphical and a numerical analysis of
#   securities (stocks, bonds, equities, and the like). Analysis
#   includes use of oscillators (Stochastic, relative_strength_indicator_rsi, and Ultimate),
#   momentum charting (Moving Average Convergence Divergence,
#   Simple and Exponential Moving Averages), trend analysis (Bands,
#   Support and Resistance, Channels), and some basic feature
#   detection (Head and Shoulders, Pennants).
#
"""
from typing import Union

# Imports from libraries
from libs.utils import start_clock

# Imports from releases
from .load_start import init_script
from .prod import run_prod
from .indexes import run_indexes
from .exports import run_exports

####################################################################
####################################################################


def technical_analysis(config: dict) -> Union[float, None]:
    """Technical Analysis

    Runs application program.

    Arguments:
        config {dict} -- app control object

    Returns:
        float -- clock time
    """
    script = init_script(config)

    if script[0] is None:
        return None

    # Start of automated process
    clock = None
    analysis, clock = run_prod(script)
    analysis, clock = run_indexes(analysis, script, clock=clock)
    run_exports(analysis, script)

    return clock


def clock_management(start_time: float) -> str:
    """ Clock management to handle elapsed time to higher levels

    Arguments:
        start_time {float} -- time of the clock

    Returns:
        str -- print out of the clock
    """
    if start_time is None:
        return 0
    elapsed = round(start_clock() - start_time)
    minutes = int(elapsed / 60)
    seconds = int(elapsed % 60)
    if minutes > 0:
        return f"{minutes}m {seconds:02d}s"
    return f"{seconds:02d}s"
