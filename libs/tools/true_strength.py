import pandas as pd 
import numpy as np 
import os

from libs.utils import generic_plotting, shape_plotting
from libs.utils import index_extractor, fund_list_extractor, dates_extractor_list, date_extractor
from libs.utils import ProgressBar
from libs.utils import api_sector_match, api_sector_funds

def basic_ratio(fundA: pd.DataFrame, fundB: pd.DataFrame) -> list:
    ratio = []

    # Mutual funds tickers update daily, several hours after close. To accomodate for any pulls of 
    # data at any time, we must know that the last [current] index may not be 'None' / 'nan'. Update
    # length of plotting to accomodate.
    tot_len = len(fundA['Adj Close']) if len(fundA['Adj Close']) <= len(fundB['Adj Close']) else len(fundB['Adj Close'])
    if pd.isna(fundA['Adj Close'][tot_len-1]) or pd.isna(fundB['Adj Close'][tot_len-1]):
        tot_len -= 1

    for close in range(tot_len):
        ratio.append(np.round(fundA['Adj Close'][close] / fundB['Adj Close'][close], 6))

    return ratio 


def normalized_ratio(fundA: pd.DataFrame, fundB: pd.DataFrame) -> list:
    ratio = []
    divisor = np.round(fundA['Adj Close'][0] / fundB['Adj Close'][0], 6)

    # Mutual funds tickers update daily, several hours after close. To accomodate for any pulls of 
    # data at any time, we must know that the last [current] index may not be 'None' / 'nan'. Update
    # length of plotting to accomodate.
    tot_len = len(fundA['Adj Close']) if len(fundA['Adj Close']) <= len(fundB['Adj Close']) else len(fundB['Adj Close'])
    if pd.isna(fundA['Adj Close'][tot_len-1]) or pd.isna(fundB['Adj Close'][tot_len-1]):
        tot_len -= 1
    
    for close in range(tot_len):
        ratio.append(np.round((fundA['Adj Close'][close] / fundB['Adj Close'][close] / divisor) - 1.0, 6))

    return ratio 


def normalized_ratio_lists(fundA: list, fundB: list) -> list:
    ratio = []
    divisor = np.round(fundA[0] / fundB[0], 6)

    # Mutual funds tickers update daily, several hours after close. To accomodate for any pulls of 
    # data at any time, we must know that the last [current] index may not be 'None' / 'nan'. Update
    # length of plotting to accomodate.
    tot_len = len(fundA) if len(fundA) <= len(fundB) else len(fundB)
    if pd.isna(fundA[tot_len-1]) or pd.isna(fundB[tot_len-1]):
        tot_len -= 1

    for close in range(tot_len):
        ratio.append(np.round((fundA[close] / fundB[close] / divisor) - 1.0, 6))

    return ratio 



def period_strength(fund_name: str, tickers: dict, periods: list, config: dict, sector: str='', sector_data: dict=None) -> list:
    """
    Try to provide ratio evaluations of 'fund' vs. market and sector
    Args:
        sector (str) - 'VGT', in the case of a tech fund
        period (list) - list of lookback periods
    Returns:
        ratio (dict)
    """
    ratio = []
    hasSP = False
    hasSector = False

    sp = get_SP500_df(tickers, config=config)
    if sp is not None:
        hasSP = True
    if sector != '':
        if sector_data is not None:
            sec = sector_data
            hasSector = True 

    fund = tickers[fund_name]

    # Mutual funds tickers update daily, several hours after close. To accomodate for any pulls of 
    # data at any time, we must know that the last [current] index may not be 'None' / 'nan'. Update
    # length of plotting to accomodate.
    mutual_fund_mode = 0
    if pd.isna(fund['Adj Close'][len(fund['Adj Close'])-1]):
        mutual_fund_mode = 1

    for period in periods:
        entry = {}
        entry['period'] = period
        entry['dates'] = date_extractor(fund.index[len(fund.index)-period], _format='str') + " : " + date_extractor(fund.index[len(fund.index)-1], _format='str')
        if hasSP:
            entry['sp500'] = {}
            sp_temp = list(sp['Adj Close'])
            sp_temp = sp_temp[len(sp_temp)-period-mutual_fund_mode:len(sp_temp)+1-mutual_fund_mode]
            f_temp = list(fund['Adj Close'])
            f_temp = f_temp[len(f_temp)-period:len(f_temp)+1]
            r = normalized_ratio_lists(f_temp, sp_temp)
            entry['sp500']['avg'] = np.round(np.mean(r), 6)
            entry['sp500']['stdev'] = np.round(np.std(r), 6)
            entry['sp500']['min'] = np.min(r) 
            entry['sp500']['max'] = np.max(r) 
            entry['sp500']['current'] = r[len(r)-1]

        if hasSector:
            entry['sector'] = {}
            entry['sector']['name'] = sector
            sp_temp = list(sec['Adj Close'])
            sp_temp = sp_temp[len(sp_temp)-period-mutual_fund_mode:len(sp_temp)+1-mutual_fund_mode]
            f_temp = list(fund['Adj Close'])
            f_temp = f_temp[len(f_temp)-period:len(f_temp)+1]
            r = normalized_ratio_lists(f_temp, sp_temp)
            entry['sector']['avg'] = np.round(np.mean(r), 6)
            entry['sector']['stdev'] = np.round(np.std(r), 6)
            entry['sector']['min'] = np.min(r) 
            entry['sector']['max'] = np.max(r) 
            entry['sector']['current'] = r[len(r)-1]

        ratio.append(entry)

    return ratio 


def get_SP500_df(tickers: dict, config: dict) -> pd.DataFrame:
    SP500_INDEX = '^GSPC' 
    if SP500_INDEX in tickers.keys():
        return tickers[SP500_INDEX]
    return None 


def relative_strength( primary_name: str, full_data_dict: dict, **kwargs ) -> dict:
    """
    Relative Strength:          Compare a fund vs. market, sector, and/or other fund

    args:
        primary_name:           (str) primary fund to compare against
        full_data_dict:         (dict) all retrieved funds by fund name

    optional args:
        secondary_fund_names:   (list) fund names to compare against; DEFAULT=[]
        meta:                   (dict) "metadata" from api calls
        config:                 (dict) control config dictionary of software package; DEFAULT=None
        sector:                 (str) sector fund (if in full_data_dict) for comparison; DEFAULT=''
        plot_output:            (bool) True to render plot in realtime; DEFAULT=True
        progress_bar:           (ProgressBar) DEFAULT=None

    returns:
        r_strength:             (dict) contains all relative strength information
    """
    secondary_fund_names = kwargs.get('secondary_fund_names', [])
    config = kwargs.get('config', None)
    sector = kwargs.get('sector', '')
    plot_output = kwargs.get('plot_output', True)
    progress_bar = kwargs.get('progress_bar', None)
    meta = kwargs.get('meta', None)
    sector_data = kwargs.get('sector_data', {})

    comp_funds = []
    comp_data = {}
    if meta is not None:
        match = meta.get('info', {}).get('sector')
        if match is not None:
            fund_len = {
                'length': len(full_data_dict[primary_name]['Close']), 
                'start': full_data_dict[primary_name].index[0], 
                'end': full_data_dict[primary_name].index[len(full_data_dict[primary_name]['Close'])-1]
            }
            match_fund, match_data = api_sector_match(match, config, fund_len=fund_len)
            if match_fund is not None:
                comp_funds, comp_data = api_sector_funds(match_fund, config, fund_len=fund_len)
                if match_data is None:
                    match_data = full_data_dict
                sector = match_fund
                sector_data = match_data

    if progress_bar is not None: progress_bar.uptick(increment=0.3)

    r_strength = dict()

    rat_sp = []
    rat_sector = [] 
    rat_secondaries = []
    secondary_names = []
    secondary_fund_names.extend(comp_funds)

    for key in comp_data.keys():
        if sector_data.get(key) is None:
            sector_data[key] = comp_data[key]

    sp = get_SP500_df(full_data_dict, config)
    if sp is not None: 
        rat_sp = normalized_ratio(full_data_dict[primary_name], sp)            
    if progress_bar is not None: progress_bar.uptick(increment=0.1)
    
    if len(sector_data) > 0:
        rat_sector = normalized_ratio(full_data_dict[primary_name], sector_data[sector])
    if progress_bar is not None: progress_bar.uptick(increment=0.1)

    if len(secondary_fund_names) > 0:
        for sfund in secondary_fund_names:
            if full_data_dict.get(sfund) is not None:
                rat_secondaries.append(normalized_ratio(full_data_dict[primary_name], full_data_dict[sfund]))
                secondary_names.append(sfund)
            elif sector_data.get(sfund) is not None:
                rat_secondaries.append(normalized_ratio(full_data_dict[primary_name], sector_data[sfund]))
                secondary_names.append(sfund)
    if progress_bar is not None: progress_bar.uptick(increment=0.2)

    st = period_strength(primary_name, full_data_dict, config=config, periods=[20, 50, 100], sector=sector, sector_data=sector_data.get(sector, None))

    r_strength['market'] = {'tabular': rat_sp, 'comparison': 'S&P500'}
    r_strength['sector'] = {'tabular': rat_sector, 'comparison': sector}
    r_strength['period'] = st
    r_strength['secondary'] = [{'tabular': second, 'comparison': secondary_names[i]} for i, second in enumerate(rat_secondaries)]
    
    dates = dates_extractor_list(full_data_dict[list(full_data_dict.keys())[0]])
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

    title = f"Relative Strength of {primary_name}"
    if progress_bar is not None: progress_bar.uptick(increment=0.1)

    if plot_output:
        generic_plotting(output_data, x=dates, title=title, legend=legend, ylabel='Difference Ratio')
    else:
        filename = primary_name +'/relative_strength_{}.png'.format(primary_name)
        generic_plotting(output_data, x=dates, title=title, saveFig=True, filename=filename, legend=legend, ylabel='Difference Ratio')

    if progress_bar is not None: progress_bar.uptick(increment=0.2)
    return r_strength
