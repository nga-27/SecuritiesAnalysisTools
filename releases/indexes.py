""" Custom Indexes """
from typing import Tuple

from libs.metrics.market_composite_index import market_composite_index
from libs.metrics.bond_composite_index import bond_composite_index
from libs.metrics.correlation_index import correlation_composite_index
from libs.metrics.type_composite_index import type_composite_index


def run_indexes(analysis: dict, script: list, clock=None) -> Tuple[dict, float]:
    """Run Indexes

    Custom indexes, such as market composite index (MCI)

    Arguments:
        analysis {dict} -- app funds data object
        script {list} -- control list: dataset, funds, periods, config

    Keyword Arguments:
        clock {uint64} -- time.time() for overall clock (default: {None})

    Returns:
        Tuple[dict, float] -- app funds data object, clock time
    """
    config = script[3]

    analysis['_METRICS_'] = {}
    analysis['_METRICS_']['mci'], data, sectors = market_composite_index(
        config=config, plot_output=False, clock=clock)

    bond_composite_index(config=config, plot_output=False, clock=clock)

    analysis['_METRICS_']['correlation'], data, sectors = correlation_composite_index(
        config=config, plot_output=False, clock=clock, data=data, sectors=sectors)

    analysis['_METRICS_']['tci'], data, sectors = type_composite_index(
        config=config, plot_output=False, clock=clock, data=data, sectors=sectors)

    return analysis, clock
