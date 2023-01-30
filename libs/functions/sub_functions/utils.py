""" utility functions for functions """
from typing import Tuple, Union

import pandas as pd

from libs.utils import (
    download_data, has_critical_error, STANDARD_COLORS, TEXT_COLOR_MAP, api_sector_match
)

TICKER = STANDARD_COLORS["ticker"]
NORMAL = STANDARD_COLORS["normal"]
WARNING = STANDARD_COLORS["warning"]

UP_COLOR = TEXT_COLOR_MAP["green"]
SIDEWAYS_COLOR = TEXT_COLOR_MAP["yellow"]
DOWN_COLOR = TEXT_COLOR_MAP["red"]


def function_data_download(config: dict, **kwargs) -> Tuple[dict, list]:
    """function_data_download

    Args:
        config (dict): configuration dictionary

    Optional Args:
        fund_list_only (bool): If True, skips downloading ticker data and returns ticker list only.
            defaults to False.

    Returns:
        Tuple[dict, list]: ticker data, fund list
    """
    fund_list_only = kwargs.get('fund_list_only', False)
    data, fund_list = download_data(config=config, fund_list_only=fund_list_only)
    if fund_list_only:
        # primarily used for VF, which downloads its own data separately.
        return {}, fund_list

    if has_critical_error(data, 'download_data'):
        return {}, []
    return data, fund_list


def function_sector_match(meta: dict,
                          fund_data: pd.DataFrame,
                          config: dict) -> Tuple[Union[str, None], Union[dict, None]]:
    """function_sector_match

    Args:
        meta (dict): metadata object
        fund_data (pd.DataFrame): ticker fund data data_frame
        config (dict): configuration dictionary

    Returns:
        Tuple[Union[str, None], Union[dict, None]]: matched name of the sector ticker, sector data
    """
    match = meta.get('info', {}).get('sector')
    if match is not None:
        fund_len = {
            'length': len(fund_data['Close']),
            'start': fund_data.index[0],
            'end': fund_data.index[
                len(fund_data['Close'])-1],
            'dates': fund_data.index
        }
        match_fund, match_data = api_sector_match(
            match, config, fund_len=fund_len,
            period=config['period'][0], interval=config['interval'][0])

        return match_fund, match_data
    return None, None
