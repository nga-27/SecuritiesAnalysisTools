import os
import json
from typing import Tuple, List, Union

from .data import download_single_fund, download_data_indexes
from .constants import STANDARD_COLORS


WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]


def api_sector_match(sector: str,
                     config: dict,
                     fund_len=None,
                     **kwargs) -> Tuple[Union[str, None], Union[dict, None]]:
    """API Sector Match

    Arguments:
        sector {str} -- sector from sectors.json
        config {dict} -- controlling configuration dictionary

    Keyword Arguments:
        fund_len {int} -- for downloading dataset (default: {None})

    Optional Args:
        period {str} -- different period than in config (default: {config['period']})
        interval {str} -- different interval than in config (default: {config['interval']})

    Returns:
        Tuple[Union[str, None], Union[dict, None]] -- 
            [matched sector fund], {data for matched sector}
    """
    period = kwargs.get('period', config['period'])
    interval = kwargs.get('interval', config['interval'])

    sector_match_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(sector_match_file):
        print(f"{WARNING}Warning: sector file '{sector_match_file}' not found.{NORMAL}")
        return None, None

    with open(sector_match_file) as f:
        matcher = json.load(f)
        matched = matcher.get("Sector", {}).get(sector)
        if matched is None:
            return None, None

        # To save downloads, if the matched items are already in the ticker list, simply use them
        tickers = config.get('tickers', '').split(' ')
        if matched in tickers:
            return matched, {}

        fund_data = download_single_fund(
            matched, config, period=period, interval=interval, fund_len=fund_len)
        return matched, fund_data


def api_sector_funds(sector_fund: str, fund_len=None, **kwargs) -> Tuple[List[str], dict]:
    """API Sector Funds

    Arguments:
        sector {str} -- sector from sectors.json

    Keyword Arguments:
        fund_len {int} -- for downloading dataset (default: {None})

    Optional Args:
        period {str} -- different period than in config (default: {'2y'})
        interval {str} -- different interval than in config (default: {'1d'})

    Returns:
        Tuple[List[str], dict] -- [Comparative funds in sector], {comparative funds ticker data}
    """
    period = kwargs.get('period', '2y')
    interval = kwargs.get('interval', '1d')

    sector_match_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(sector_match_file):
        print(
            f"{WARNING}Warning: sector file '{sector_match_file}' not found.{NORMAL}")
        return [], {}

    if sector_fund is None:
        return [], {}

    with open(sector_match_file) as f:
        matcher = json.load(f)
        matched = matcher.get("Comparison", {}).get(sector_fund)

        if matched is None:
            return [], {}

        tickers = ' '.join(matched)
        fund_data, _ = download_data_indexes(
            indexes=matched, tickers=tickers, fund_len=fund_len, period=period, interval=interval)
        return matched, fund_data
