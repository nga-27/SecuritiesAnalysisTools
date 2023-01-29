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


def function_data_download(config: dict, **kwargs) -> list:
    fund_list_only = kwargs.get('fund_list_only', False)
    data, fund_list = download_data(config=config, fund_list_only=fund_list_only)
    if fund_list_only:
        # primarily used for VF, which downloads its own data separately.
        return {}, fund_list

    e_check = {'tickers': config['tickers']}
    if has_critical_error(data, 'download_data', misc=e_check):
        return {}, []
    return data, fund_list


def function_sector_match(meta: dict, fund_data: pd.DataFrame, config: dict) -> dict:
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
