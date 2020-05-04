"""
#   Technical Analysis Tools
#
#   by: nga-27
#
#   A program that outputs a graphical and a numerical analysis of
#   securities (stocks, bonds, equities, and the like). Analysis 
#   includes use of oscillators (Stochastic, RSI, and Ultimate), 
#   momentum charting (Moving Average Convergence Divergence, 
#   Simple and Exponential Moving Averages), trend analysis (Bands, 
#   Support and Resistance, Channels), and some basic feature 
#   detection (Head and Shoulders, Pennants).
#   
"""

# Imports from libraries
from libs.utils import start_clock

# Imports from releases
from .load_start import init_script
from .dev import run_dev
from .prod import run_prod
from .indexes import run_indexes
from .exports import run_exports

####################################################################
####################################################################


def technical_analysis(config: dict, release='prod'):
    """Technical Analysis

    Runs application program, funneling to either 'dev' or 'prod', metrics, etc.

    Arguments:
        config {dict} -- app control object

    Keyword Arguments:
        release {str} -- either 'dev' or 'prod' (default: {'prod'})
    """
    script = init_script(config, release=release)

    if script is None:
        return

    # Start of automated process
    clock = None
    if release == 'dev':
        analysis, clock = run_dev(script)
    else:
        analysis, clock = run_prod(script)

    analysis, clock = run_indexes(analysis, script, clock=clock)
    run_exports(analysis, script)

    return clock


def clock_management(start_time: float):
    """ Clock management to handle elapsed time to higher levels """
    elapsed = round(start_clock() - start_time)
    return elapsed
