import pandas as pd 
import numpy as np 
import os

from libs.utils import generic_plotting, shape_plotting
from libs.utils import index_extractor, fund_list_extractor, dates_extractor_list, date_extractor

# Relative strength ratio 

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



def period_strength(fund_name: str, tickers: dict, periods: list, config: dict, sector: str='') -> list:
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
        if sector in tickers.keys():
            sec = tickers[sector]
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


def is_fund_match(fundA: pd.DataFrame, fundB: pd.DataFrame) -> bool:
    lenA = len(fundA['Close'])
    lenB = len(fundB['Close'])
    if lenA == lenB:
        indCheck = int(np.floor(float(lenA)/3.0))
        if fundA['Close'][indCheck] == fundB['Close'][indCheck]:
            indCheck = int(np.floor(float(lenA) / 4.0 * 3.0))
            if fundA['Open'][indCheck] == fundB['Open'][indCheck]:
                return True
    return False 


def relative_strength( fundA_name: str,  
    full_data_dict: dict,
    fundB_name: str='',
    config: dict=None,
    sector: str='', 
    plot_output=True ) -> list:

    if fundB_name == '':
        fundB_name = fundA_name
    positionB = full_data_dict[fundB_name]
    title = 'Strength: {} - {}'.format(fundA_name, fundB_name)
    if sector == '':
        sp = get_SP500_df(full_data_dict, config)
        if sp is not None and is_fund_match(full_data_dict[fundA_name], full_data_dict[fundB_name]):
            positionB = sp 
            title = 'Strength: {} vs. ^GSPC'.format(fundA_name)
            
    rat = normalized_ratio(full_data_dict[fundA_name], positionB)
    st = period_strength(fundA_name, full_data_dict, config=config, periods=[20, 50, 100], sector=sector)
    
    # Mutual funds tickers update daily, several hours after close. To accomodate for any pulls of 
    # data at any time, we must know that the last [current] index may not be 'None' / 'nan'. Update
    # length of plotting to accomodate.
    dates = dates_extractor_list(full_data_dict[list(full_data_dict.keys())[0]])
    if len(rat) < len(dates):
        dates = dates[0:len(rat)]

    if plot_output:
        generic_plotting([rat], x_=dates, title=title)
    else:
        filename = fundA_name +'/relative_strength_{}.png'.format(fundA_name)
        generic_plotting([rat], x_=dates, title=title, saveFig=True, filename=filename)

    return st
