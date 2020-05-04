from libs.metrics import market_composite_index
from libs.metrics import bond_composite_index
from libs.metrics import correlation_composite_index
from libs.metrics import type_composite_index


def run_indexes(analysis: dict, script: list, clock=None) -> dict:
    """Run Indexes

    Custom indexes, such as market composite index (MCI)

    Arguments:
        analysis {dict} -- app funds data object
        script {list} -- control list: dataset, funds, periods, config

    Keyword Arguments:
        clock {uint64} -- time.time() for overall clock (default: {None})

    Returns:
        [dict] -- app funds data object
    """
    config = script[3]

    analysis['_METRICS_'] = {}
    analysis['_METRICS_']['mci'] = market_composite_index(
        config=config, plot_output=False, clock=clock)

    bond_composite_index(config=config, plot_output=False, clock=clock)

    analysis['_METRICS_']['correlation'] = correlation_composite_index(
        config=config, plot_output=False, clock=clock)

    analysis['_METRICS_']['tci'] = type_composite_index(
        config=config, plot_output=False, clock=clock)

    return analysis, clock
