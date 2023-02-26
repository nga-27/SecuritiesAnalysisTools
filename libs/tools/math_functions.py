""" math functions """
from typing import Tuple, Union

import pandas as pd
import numpy as np

from scipy.stats import linregress


def lower_low(data: Union[list, pd.DataFrame], start_val: float, start_ind: int) -> list:
    """Lower Low

    Looks for a bounce (rise) then lower low

    Arguments:
        data {list} -- price data
        start_val {float} -- a low to find a lower
        start_ind {int} -- starting index where the low exists

    Returns:
        list - [lower_value, respective_index]
    """
    data = list(data)
    track_ind = start_ind
    track_val = start_val

    # 0: first descent or rise; 1: lower low (in progress); 2: rise (lowest low found/not found)
    bounce_state = 0
    lows = []

    for price in range(start_ind, len(data)):
        if (data[price] < start_val) and (bounce_state < 2):
            track_ind = price
            track_val = data[price]
            bounce_state = 1

        if (data[price] > track_val) and (bounce_state == 1):
            bounce_state = 2

        if (data[price] < track_val) and (bounce_state > 1):
            bounce_state = 3
            track_ind = price
            track_val = data[price]

        if (data[price] > track_val) and (bounce_state == 3):
            bounce_state = 4
            lows.append([track_val, track_ind])

    return lows


def higher_high(data: Union[list, pd.DataFrame], start_val: float, start_ind: int) -> list:
    """Higher High

    Looks for a bounce (drop) then higher high

    Arguments:
        data {list} -- price data
        start_val {float} -- a low to find a lower
        start_ind {int} -- starting index where the low exists

    Returns:
        list - [lower_value, respective_index]
    """
    data = list(data)
    track_ind = start_ind
    track_val = start_val

    # 0: first descent or rise; 1: lower low (in progress); 2: rise (lowest low found/not found)
    bounce_state = 0
    highs = []

    for price in range(start_ind, len(data)):

        if (data[price] > start_val) and (bounce_state < 2):
            track_ind = price
            track_val = data[price]
            bounce_state = 1

        if (data[price] < track_val) and (bounce_state == 1):
            bounce_state = 2

        if (data[price] > track_val) and (bounce_state > 1):
            bounce_state = 3
            track_ind = price
            track_val = data[price]

        if (data[price] < track_val) and (bounce_state == 3):
            bounce_state = 4
            highs.append([track_val, track_ind])

    return highs


def bull_bear_th(osc: list, start: int, thresh: float, bull_bear: str = 'bull') -> Union[int, None]:
    """Bull Bear Thresholding

    Arguments:
        osc {list} -- oscillator signal
        start {int} -- starting index to find the threshold
        thresh {float} -- threshold for comparison

    Keyword Arguments:
        bull_bear {str} -- type, either 'bull' or 'bear' (default: {'bull'})

    Returns:
        int -- index that is above/below threshold
    """
    count = start
    if bull_bear == 'bull':
        while count < len(osc):
            if osc[count] > thresh:
                return count
            count += 1

    if bull_bear == 'bear':
        while count < len(osc):
            if osc[count] < thresh:
                return count
            count += 1

    return None


def beta_comparison(fund: pd.DataFrame, benchmark: pd.DataFrame) -> Tuple[float, float]:
    """Beta Comparison

    Arguments:
        fund {pd.DataFrame} -- fund historical data
        benchmark {pd.DataFrame} -- a particular benchmark's fund historical data

    Returns:
        list -- beta {float}, r-squared {float}
    """
    tot_len = len(fund['Close'])
    if pd.isna(fund['Close'][len(fund['Close'])-1]):
        tot_len -= 1

    fund_return = []
    fund_return.append(0.0)
    bench_return = []
    bench_return.append(0.0)
    for i in range(1, tot_len):
        ret = (fund['Close'][i]-fund['Close'][i-1]) / \
            fund['Close'][i-1] * 100.0
        fund_return.append(ret)
        ret = (benchmark['Close'][i]-benchmark['Close']
               [i-1]) / benchmark['Close'][i-1] * 100.0
        bench_return.append(ret)

    # slope, intercept, r-correlation, p-value, stderr
    slope, _, r_value, _, _ = linregress(bench_return, fund_return)
    r_sqd = r_value ** 2

    return slope, r_sqd


def beta_comparison_list(fund: list, benchmark: list) -> Tuple[float, float]:
    """Beta Comparison List

    Like above, but compares entire list versus a benchmark

    Arguments:
        fund {list} -- list of the fund to compare
        benchmark {list} -- list of the benchmark, such as S&P500

    Returns:
        list -- beta, r-squared
    """
    tot_len = len(fund)

    fund_return = []
    fund_return.append(0.0)
    bench_return = []
    bench_return.append(0.0)
    for i in range(1, tot_len):
        ret = (fund[i]-fund[i-1]) / fund[i-1] * 100.0
        fund_return.append(ret)
        ret = (benchmark[i]-benchmark[i-1]) / benchmark[i-1] * 100.0
        bench_return.append(ret)

    # slope, intercept, r-correlation, p-value, stderr
    slope, _, r_value, _, _ = linregress(bench_return, fund_return)
    r_sqd = r_value ** 2

    return slope, r_sqd


def risk_comparison(fund: pd.DataFrame,
                    benchmark: pd.DataFrame,
                    treasury: pd.DataFrame,
                    beta: float = None,
                    rsqd: float = None,
                    **kwargs) -> dict:
    """Risk Comparison

    Alpha metric, with Sharpe Ratio, Beta, R-Squared, and Standard Deviation

    Arguments:
        fund {pd.DataFrame} -- fund dataset
        benchmark {pd.DataFrame} -- benchmark dataset (does not have to be SP500)
        treasury {pd.DataFrame} -- 11-week treasury bill dataset

    Keyword Arguments:
        beta {float} -- beta figure; will calculate if None (default: {None})
        rsqd {float} -- r-squared figure; will calculate if None (default: {None})

    Optional Args:
        print_out {bool} -- prints risk ratios to terminal (default: {False})
        sector_data {pd.DataFrame} -- data of related sector (default: {None})

    Returns:
        dict -- alpha data object
    """
    # pylint: disable=too-many-locals,too-many-statements
    print_out = kwargs.get('print_out', False)
    sector_data = kwargs.get('sector_data')

    alpha = {}
    if beta is None or rsqd is None:
        beta, rsqd = beta_comparison(fund, benchmark)

    beta = np.round(beta, 4)
    rsqd = np.round(rsqd, 4)

    fund_return, fund_stdev = get_returns(fund)
    bench_return, bench_stdev = get_returns(benchmark)
    treas_return = treasury['Close'][-1]

    alpha_sector = "n/a"
    beta_sector = "n/a"
    rsqd_sector = "n/a"
    sharpe_ratio = "n/a"
    market_sharpe = "n/a"

    if sector_data is not None:
        sector_return, _ = get_returns(sector_data)
        beta_sector, rsqd_sector = beta_comparison(fund, sector_data)
        beta_sector = np.round(beta_sector, 4)
        rsqd_sector = np.round(rsqd_sector, 4)
        alpha_sector = np.round(fund_return - treas_return -
                                beta_sector * (sector_return - treas_return), 4)

    alpha_val = np.round(fund_return - treas_return -
                         beta * (bench_return - treas_return), 4)

    if fund_stdev != 0.0:
        sharpe_ratio = np.round((fund_return - treas_return) / fund_stdev, 4)
        if bench_stdev != 0.0:
            bench_sharpe = np.round((bench_return - treas_return) / bench_stdev, 4)
            market_sharpe = np.round(sharpe_ratio / bench_sharpe, 4)

    fund_stdev = np.round(fund_stdev, 4)

    alpha['alpha'] = {"market": alpha_val}
    alpha['beta'] = {"market": beta}
    alpha['r_squared'] = {"market": rsqd}
    alpha['sharpe'] = sharpe_ratio
    alpha['market_sharpe'] = market_sharpe
    alpha['standard_deviation'] = fund_stdev
    alpha['returns'] = {
        'fund': fund_return,
        'benchmark': bench_return,
        'treasury': treas_return
    }

    _, _, fund_interval_std = get_interval_standard_dev(fund)
    _, _, bench_interval_std = get_interval_standard_dev(benchmark)

    alpha['standard_dev_ratio'] = np.round(fund_interval_std/bench_interval_std, 4)

    if sector_data is not None:
        alpha['returns']["sector"] = sector_return
        alpha['alpha']["sector"] = alpha_sector
        alpha['beta']["sector"] = beta_sector
        alpha['r_squared']["sector"] = rsqd_sector

    if print_out:
        print("\r\n")
        print(f"\r\nAlpha Market:\t\t{alpha_val}")
        print(f"Alpha Sector:\t\t{alpha_sector}")
        print(f"Beta Market:\t\t{beta}")
        print(f"Beta Sector:\t\t{beta_sector}")
        print(f"R-Squared Market:\t{rsqd}")
        print(f"R-Squared Sector:\t{rsqd_sector}")
        print(f"Sharpe Ratio:\t\t{sharpe_ratio}")
        print(f"Market Sharpe:\t\t{market_sharpe}")
        print(f"Standard Dev:\t\t{fund_stdev}")
        print(f"Market Ratio SD:\t{alpha['standard_dev_ratio']}")

    return alpha


def get_returns(data: pd.DataFrame, output: str = 'annual') -> Union[float, float]:
    """Get Returns

    Arguments:
        data {pd.DataFrame} -- fund dataset

    Keyword Arguments:
        output {str} -- return for a period (default: {'annual'})

    Returns:
        list -- return, standard deviation
    """
    # pylint: disable=too-many-locals
    # Determine intervals for returns, start with annual
    interval = 250

    years = int(len(data['Close']) / interval)
    if years == 0:
        years = 1
    quarters = 4 * years

    if len(data['Close']) <= interval:
        interval = 200

    annual_returns = 0.0
    annual_std = []
    for i in range(years):
        ars = (data['Adj Close'][(i+1) * interval] - data['Adj Close']
               [i * interval]) / data['Adj Close'][i * interval] * 100.0
        annual_returns += ars
        annual_std.append(ars)

    annual_returns /= float(years)
    annual_returns = (data['Adj Close'][-1] - data['Adj Close']
                      [-interval]) / data['Adj Close'][-interval] * 100.0

    # Determine intervals for returns, next with quarterly
    q_returns = 0.0
    q_std = []
    qrs_2 = 0.0
    counter = 0
    for i in range(quarters):
        multiple = 62
        if i % 2 != 0:
            multiple = 63
        counter += multiple

        qrs = (data['Adj Close'][counter] - data['Adj Close']
               [counter - multiple]) / data['Adj Close'][counter - multiple] * 100.0
        q_returns += qrs
        qrs_2 += qrs
        if i % 4 == 3:
            q_std.append(qrs_2)
            qrs_2 = 0.0

    q_returns /= float(quarters)
    q_returns *= 4.0

    q_returns = 0.0
    for i in range(4):
        start = -1 + -1 * int(62.5 * float(i))
        subtract = -1 * int(62.5 * float(i + 1))
        qrs = (data['Adj Close'][start] - data['Adj Close']
               [subtract]) / data['Adj Close'][subtract] * 100.0
        q_returns += qrs

    std_1 = np.std(annual_std)
    std_2 = np.std(q_std)

    returns = np.mean([q_returns, annual_returns])
    st_devs = np.mean([std_1, std_2])
    if output == 'quarterly':
        returns /= 4.0

    return returns, st_devs


def get_interval_standard_dev(data: pd.DataFrame, interval: int=250) -> Tuple[float, float, float]:
    """get_return_standard_dev

    Mean, Median, Std of return rates from day-to-day

    Args:
        data (pd.DataFrame): fund dataset
        interval (int, optional): trading periods. Defaults to 250.

    Returns:
        Tuple[float, float, float]: mean, median, std
    """
    data_slice = data['Adj Close'][-interval:]
    returns = [0.0] * len(data_slice)
    for i in range(1, len(data_slice)):
        returns[i] = (data_slice[i] - data_slice[i-1]) / data_slice[i-1]

    return np.mean(returns), np.median(returns), np.std(returns)
