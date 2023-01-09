import os
import pandas as pd
import numpy as np

from libs.utils import (
    generic_plotting, dates_extractor_list, date_extractor, 
    INDEXES, api_sector_match, api_sector_funds
)


def normalized_ratio(fundA, fundB, data_type: str = 'dataframe', key: str = 'Adj Close') -> list:
    """Normalized Ratio

    Handles both pd.DataFrames (default) and list comparisons

    Arguments:
        fundA {pd.DataFrame, list} -- fund A to compare
        fundB {pd.DataFrame, list} -- fund B to compare

    Keyword Arguments:
        data_type {str} -- type of data type, pd.DataFrame or list (default: {'dataframe'})
        key {str} -- if pd.DataFrame, column key (default: {'Adj Close'})

    Returns:
        list -- normalized ratio list of A/B
    """
    ratio = []

    if data_type == 'dataframe':
        divisor = np.round(fundA[key][0] / fundB[key][0], 6)
        for i, close in enumerate(fundA[key]):
            ratio.append(np.round(
                (close / fundB[key][i] / divisor) - 1.0, 6))

    elif data_type == 'list':
        divisor = np.round(fundA[0] / fundB[0], 6)
        for i, close in enumerate(fundA):
            ratio.append(
                np.round((close / fundB[i] / divisor) - 1.0, 6))

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
    sector = kwargs.get('sector', '')
    sector_data = kwargs.get('sector_data')

    ratio = []
    hasSP = False
    hasSector = False

    sp = get_SP500_df(tickers)
    if sp is not None:
        hasSP = True
    if sector != '':
        if sector_data is not None:
            sec = sector_data
            hasSector = True

    fund = tickers[fund_name]

    for period in periods:
        entry = {}

        entry['period'] = period
        entry['dates'] = date_extractor(fund.index[len(fund.index)-period], _format='str') + \
            " : " + \
            date_extractor(fund.index[len(fund.index)-1], _format='str')

        if hasSP:
            entry['sp500'] = {}

            sp_temp = list(sp['Adj Close'])
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

        if hasSector:
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


def get_SP500_df(tickers: dict) -> pd.DataFrame:
    """Get S&P500 DataFrame

    Simple way of getting the S&P-specific frame from the data dict.

    Arguments:
        tickers {dict} -- entire data object

    Returns:
        pd.DataFrame -- S&P500-specific DataFrame
    """
    SP500_INDEX = '^GSPC'
    if SP500_INDEX in tickers:
        return tickers[SP500_INDEX]
    return None


def relative_strength(primary_name: str, full_data_dict: dict, **kwargs) -> list:
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
    secondary_fund_names = kwargs.get('secondary_fund_names', [])
    config = kwargs.get('config', None)
    sector = kwargs.get('sector', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar = kwargs.get('progress_bar', None)
    meta = kwargs.get('meta', None)
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
                elif match_data == {}:
                    match_data = full_data_dict[match_fund]
                sector = match_fund
                sector_data = match_data
                sector_bench = match_data[match_fund]

    if progress_bar is not None:
        progress_bar.uptick(increment=0.3)

    r_strength = dict()

    rat_sp = []
    rat_sector = []
    rat_secondaries = []
    secondary_names = []
    secondary_fund_names.extend(comp_funds)

    for key in comp_data:
        if sector_data.get(key) is None:
            sector_data[key] = comp_data[key]

    sp = get_SP500_df(full_data_dict)
    if sp is not None:
        rat_sp = normalized_ratio(full_data_dict[primary_name], sp)
    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    if len(sector_data) > 0:
        rat_sector = normalized_ratio(
            full_data_dict[primary_name], sector_data[sector])
    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

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

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    st = period_strength(primary_name,
                         full_data_dict,
                         config=config,
                         periods=[20, 50, 100],
                         sector=sector,
                         sector_data=sector_data.get(sector, None))

    r_strength['market'] = {'tabular': rat_sp, 'comparison': 'S&P500'}
    r_strength['sector'] = {'tabular': rat_sector, 'comparison': sector}
    r_strength['period'] = st
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

    if progress_bar is not None:
        progress_bar.uptick(increment=0.1)

    if plot_output:
        generic_plotting(output_data, x=dates, title=title,
                         legend=legend, ylabel='Difference Ratio')

    else:
        filename = os.path.join(
            primary_name, view, f"relative_strength_{primary_name}.png")
        generic_plotting(output_data,
                         x=dates,
                         title=title,
                         save_fig=True,
                         filename=filename,
                         legend=legend,
                         ylabel='Difference Ratio')

    if progress_bar is not None:
        progress_bar.uptick(increment=0.2)

    return r_strength, sector_bench
