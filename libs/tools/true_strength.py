import pandas as pd 
import numpy as np 
import os

from libs.utils import generic_plotting

# Relative strength ratio 
SP500_INDEX = 'securities/^GSPC.csv'

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



def period_strength(fund: pd.DataFrame, periods: list, sector: str='') -> list:
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

    if os.path.exists(SP500_INDEX):
        sp = pd.read_csv(SP500_INDEX)
        hasSP = True
    if len(sector) > 0:
        filename = 'securities/' + sector + '.csv'
        if os.path.exists(filename):
            sec = pd.read_csv(filename)
            hasSector = True 

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


def get_SP500() -> pd.DataFrame:
    if os.path.exists(SP500_INDEX):
        sp = pd.read_csv(SP500_INDEX)
        return sp 
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


def relative_strength(positionA: pd.DataFrame, positionB: pd.DataFrame, sector: str='', plot_output=True) -> list:
    if sector == '':
        sp = get_SP500()
        if sp is not None and is_fund_match(positionA, positionB):
            positionB = sp 
    rat = normalized_ratio(positionA, positionB)
    st = period_strength(positionA, periods=[20, 50, 100], sector=sector)
    
    if plot_output:
        generic_plotting([rat], 'Strength of Fund')
        #plt.plot(rat)
        #plt.title('Strength of Fund')
        #plt.show()

    return st
