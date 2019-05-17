import pandas as pd 
import numpy as np 
import os

from libs.utils import generic_plotting
from libs.utils import index_extractor, fund_list_extractor, dates_extractor_list

# Relative strength ratio 

def basic_ratio(fundA: pd.DataFrame, fundB: pd.DataFrame) -> list:
    ratio = []
    for close in range(len(fundA['Adj Close'])):
        ratio.append(np.round(fundA['Adj Close'][close] / fundB['Adj Close'][close], 6))

    return ratio 


def normalized_ratio(fundA: pd.DataFrame, fundB: pd.DataFrame) -> list:
    ratio = []
    divisor = np.round(fundA['Adj Close'][0] / fundB['Adj Close'][0], 6)
    for close in range(len(fundA['Adj Close'])):
        ratio.append(np.round((fundA['Adj Close'][close] / fundB['Adj Close'][close] / divisor) - 1.0, 6))

    return ratio 


def normalized_ratio_lists(fundA: list, fundB: list) -> list:
    ratio = []
    divisor = np.round(fundA[0] / fundB[0], 6)
    for close in range(len(fundA)):
        ratio.append(np.round((fundA[close] / fundB[close] / divisor) - 1.0, 6))

    return ratio 



def period_strength(fund_name: str, tickers: pd.DataFrame, periods: list, sector: str='') -> list:
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

    sp = get_SP500(tickers)
    if sp is not None:
        hasSP = True
    if sector != '':
        if sector in tickers.keys():
            sec = tickers[sector]
            hasSector = True 

    fund = tickers[fund_name]

    for period in periods:
        entry = {}
        entry['period'] = period
        entry['dates'] = str(fund.index[len(fund.index)-period]) + " : " + str(fund.index[len(fund.index)-1]) 
        if hasSP:
            entry['sp500'] = {}
            sp_temp = list(sp['Adj Close'])
            sp_temp = sp_temp[len(sp_temp)-period:len(sp_temp)+1]
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
            sp_temp = sp_temp[len(sp_temp)-period:len(sp_temp)+1]
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


def get_SP500(tickers: pd.DataFrame) -> pd.DataFrame:
    SP500_INDEX = 'securities/^GSPC.csv'
    if os.path.exists(SP500_INDEX):
        sp = pd.read_csv(SP500_INDEX)
        return sp 
    sp = index_extractor(fund_list_extractor(tickers))
    if sp is not None:
        return tickers[sp]
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
    fundB_name: str, 
    tickers: pd.DataFrame,
    sector: str='', 
    plot_output=True ) -> list:

    positionB = tickers[fundB_name]
    if sector == '':
        sp = get_SP500(tickers)
        if sp is not None and is_fund_match(tickers[fundA_name], tickers[fundB_name]):
            positionB = sp 
    rat = normalized_ratio(tickers[fundA_name], positionB)
    st = period_strength(fundA_name, tickers, periods=[20, 50, 100], sector=sector)
    
    title = 'Strength: {} - {}'.format(fundA_name, fundB_name)
    dates = dates_extractor_list(tickers)
    if plot_output:
        generic_plotting([rat], x_=dates, title=title)
    else:
        filename = fundA_name +'/relative_strength_{}.png'.format(fundA_name)
        generic_plotting([rat], x_=dates, title=title, saveFig=True, filename=filename)

    return st
