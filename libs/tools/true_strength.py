""" True Strength """
import os
from typing import Union, Tuple

import pandas as pd
import numpy as np

from libs.utils.progress_bar import ProgressBar, update_progress_bar
from libs.utils import (
    generate_plot, PlotType, dates_extractor_list, date_extractor,
    INDEXES, api_sector_match, api_sector_funds
)


def normalized_ratio(fund_a: Union[dict, pd.DataFrame], fund_b: Union[dict, pd.DataFrame],
                     data_type: str = 'dataframe', key: str = 'Adj Close') -> list:
    """Normalized Ratio

    Handles both pd.DataFrames (default) and list comparisons

    Arguments:
        fund_a {pd.DataFrame, list} -- fund A to compare
        fundB {pd.DataFrame, list} -- fund B to compare

    Keyword Arguments:
        data_type {str} -- type of data type, pd.DataFrame or list (default: {'dataframe'})
        key {str} -- if pd.DataFrame, column key (default: {'Adj Close'})

    Returns:
        list -- normalized ratio list of A/B
    """
    ratio = []
    if data_type == 'dataframe':
        divisor = np.round(fund_a[key][0] / fund_b[key][0], 6)
        for i, close in enumerate(fund_a[key]):
            ratio.append(np.round((close / fund_b[key][i] / divisor) - 1.0, 6))

    elif data_type == 'list':
        divisor = np.round(fund_a[0] / fund_b[0], 6)
        for i, close in enumerate(fund_a):
            ratio.append(np.round((close / fund_b[i] / divisor) - 1.0, 6))

    return ratio


def period_strength(fund_name: str, tickers: dict, periods: list, **kwargs) -> list:
    """Period Strength

    Try to provide ratio evaluations of 'fund' vs. market and sector. Update utilizes sectors.json
    file to pull information.

    Arguments:
        fund_name {str} -- 'MSFT', for example
        tickers {dict} -- entire downloaded data object
        periods {list} - list of lookback periods

    Optional Args:
        sector {str} -- name of sector, 'VGT' for Tech, for example (default: {''})
        sector_data {pd.DataFrame} -- data of sector (default: {None})

    Returns:
        list -- list of ratio data objects
    """
    # pylint: disable=too-many-locals
    sector = kwargs.get('sector', '')
    sector_data = kwargs.get('sector_data')

    ratio = []
    has_sp = False
    has_sector = False

    sp_500_data = tickers.get('^GSPC')
    if sp_500_data is not None:
        has_sp = True
    if sector != '':
        if sector_data is not None:
            sec = sector_data
            has_sector = True

    fund = tickers[fund_name]
    for period in periods:
        entry = {}
        entry['period'] = period
        entry['dates'] = date_extractor(fund.index[len(fund.index)-period], _format='str') + \
            " : " + \
            date_extractor(fund.index[len(fund.index)-1], _format='str')

        if has_sp:
            entry['sp500'] = {}

            sp_temp = list(sp_500_data['Adj Close'])
            sp_temp = sp_temp[len(
                sp_temp)-period:len(sp_temp)+1]

            f_temp = list(fund['Adj Close'])
            f_temp = f_temp[len(f_temp)-period:len(f_temp)+1]

            rat = normalized_ratio(f_temp, sp_temp, data_type='list')

            entry['sp500']['avg'] = np.round(np.mean(rat), 6)
            entry['sp500']['stdev'] = np.round(np.std(rat), 6)
            entry['sp500']['min'] = np.min(rat)
            entry['sp500']['max'] = np.max(rat)
            entry['sp500']['current'] = rat[-1]

        if has_sector:
            entry['sector'] = {}
            entry['sector']['name'] = sector

            sp_temp = list(sec['Adj Close'])
            sp_temp = sp_temp[len(
                sp_temp)-period:len(sp_temp)+1]

            f_temp = list(fund['Adj Close'])
            f_temp = f_temp[len(f_temp)-period:len(f_temp)+1]

            rat = normalized_ratio(f_temp, sp_temp, data_type='list')

            entry['sector']['avg'] = np.round(np.mean(rat), 6)
            entry['sector']['stdev'] = np.round(np.std(rat), 6)
            entry['sector']['min'] = np.min(rat)
            entry['sector']['max'] = np.max(rat)
            entry['sector']['current'] = rat[-1]

        ratio.append(entry)

    return ratio


def relative_strength(primary_name: str, full_data_dict: dict,
                      **kwargs) -> Tuple[dict, Union[dict, None]]:
    """Relative Strength

    Compare a fund vs. market, sector, and/or other fund

    Arguments:
        primary_name {str} -- primary fund to compare against
        full_data_dict {dict} -- all retrieved funds by fund name

    Optional Args:
        secondary_fund_names {list} -- fund names to compare against (default: {[]})
        meta {dict} -- "metadata" from api calls (default: {None})
        config {dict} -- control config dictionary of software package (default: {None})
        sector {str} -- sector fund (if in full_data_dict) for comparison (default: {''})
        plot_output {bool} -- True to render plot in realtime (default: {True})
        progress_bar {ProgressBar} -- (default: {None})
        view {str} -- Directory of plots (default: {''})

    Returns:
        list -- dict containing all relative strength information, sector match data
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    secondary_fund_names = kwargs.get('secondary_fund_names', [])
    config = kwargs.get('config')
    sector = kwargs.get('sector', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar: Union[ProgressBar, None] = kwargs.get('progress_bar')
    meta = kwargs.get('meta')
    sector_data = kwargs.get('sector_data', {})
    view = kwargs.get('view', '')

    period = kwargs.get('period', '2y')
    interval = kwargs.get('interval', '1d')

    sector_bench = None
    comp_funds = []
    comp_data = {}
    if meta is not None:
        match = meta.get('info', {}).get('sector')

        if match is not None:
            fund_len = {
                'length': len(full_data_dict[primary_name]['Close']),
                'start': full_data_dict[primary_name].index[0],
                'end': full_data_dict[primary_name].index[
                    len(full_data_dict[primary_name]['Close'])-1],
                'dates': full_data_dict[primary_name].index
            }

            match_fund, match_data = api_sector_match(
                match, config, fund_len=fund_len, period=period, interval=interval)

            if match_fund is not None:
                comp_funds, comp_data = api_sector_funds(
                    match_fund, fund_len=fund_len, period=period, interval=interval)

                if match_data is None:
                    match_data = full_data_dict
                elif not match_data:
                    match_data = full_data_dict[match_fund]
                sector = match_fund
                sector_data = match_data
                sector_bench = match_data[match_fund]

    update_progress_bar(progress_bar, 0.3)

    r_strength = {}
    rat_sp = []
    rat_sector = []
    rat_secondaries = []
    secondary_names = []
    secondary_fund_names.extend(comp_funds)

    for key, content in comp_data.items():
        if content is None:
            sector_data[key] = comp_data[key]

    sp_500_data = full_data_dict.get('^GSPC')
    if sp_500_data is not None:
        rat_sp = normalized_ratio(full_data_dict[primary_name], sp_500_data)
    update_progress_bar(progress_bar, 0.1)

    if len(sector_data) > 0:
        rat_sector = normalized_ratio(
            full_data_dict[primary_name], sector_data[sector])
    update_progress_bar(progress_bar, 0.1)

    if len(secondary_fund_names) > 0:
        for sfund in secondary_fund_names:
            if full_data_dict.get(sfund) is not None:
                rat_secondaries.append(normalized_ratio(
                    full_data_dict[primary_name], full_data_dict[sfund]))
                secondary_names.append(sfund)

            elif sector_data.get(sfund) is not None:
                rat_secondaries.append(normalized_ratio(
                    full_data_dict[primary_name], sector_data[sfund]))
                secondary_names.append(sfund)

    update_progress_bar(progress_bar, 0.2)

    p_strength = period_strength(primary_name,
                                full_data_dict,
                                config=config,
                                periods=[20, 50, 100],
                                sector=sector,
                                sector_data=sector_data.get(sector, None))

    r_strength['market'] = {'tabular': rat_sp, 'comparison': 'S&P500'}
    r_strength['sector'] = {'tabular': rat_sector, 'comparison': sector}
    r_strength['period'] = p_strength
    r_strength['secondary'] = [{'tabular': second, 'comparison': secondary_names[i]}
                               for i, second in enumerate(rat_secondaries)]

    dates = dates_extractor_list(
        full_data_dict[list(full_data_dict.keys())[0]])
    if len(rat_sp) < len(dates):
        dates = dates[0:len(rat_sp)]

    output_data = []
    legend = []
    if len(rat_sp) > 0:
        output_data.append(rat_sp)
        legend.append("vs. S&P 500")

    if len(rat_sector) > 0:
        output_data.append(rat_sector)
        legend.append(f"vs. Sector ({sector})")

    if len(rat_secondaries) > 0:
        for i, rat in enumerate(rat_secondaries):
            output_data.append(rat)
            legend.append(f"vs. {secondary_names[i]}")

    r_strength['tabular'] = {}
    for i, out_data in enumerate(output_data):
        r_strength['tabular'][str(legend[i])] = out_data

    primary_name2 = INDEXES.get(primary_name, primary_name)
    title = f"Relative Strength of {primary_name2}"

    update_progress_bar(progress_bar, 0.1)
    generate_plot(
        PlotType.GENERIC_PLOTTING, output_data, **{
            "x": dates, "title": title, "save_fig": True, "legend": legend,
            "ylabel": 'Difference Ratio',
            "plot_output": plot_output,
            "filename": os.path.join(primary_name, view, f"relative_strength_{primary_name}.png")
        }
    )

    update_progress_bar(progress_bar, 0.2)
    return r_strength, sector_bench
