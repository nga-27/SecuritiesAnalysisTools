import pandas as pd
import numpy as np
from scipy.stats import linregress


def lower_low(data, start_val: float, start_ind: int) -> list:
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


def higher_high(data, start_val: float, start_ind: int) -> list:
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


def bull_bear_th(osc: list, start: int, thresh: float, bull_bear='bull'):
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


def beta_comparison(fund: pd.DataFrame, benchmark: pd.DataFrame) -> list:
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
    beta_figures = linregress(bench_return, fund_return)
    rsqd = beta_figures[2]**2

    return beta_figures[0], rsqd


def beta_comparison_list(fund: list, benchmark: list) -> list:
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
    beta_figures = linregress(bench_return, fund_return)
    rsqd = beta_figures[2]**2

    return beta_figures[0], rsqd


def alpha_comparison(fund: pd.DataFrame,
                     benchmark: pd.DataFrame,
                     treasury: pd.DataFrame,
                     beta: float = None) -> dict:

    alpha = dict()
    if beta is None:
        beta, _ = beta_comparison(fund, benchmark)

    fund_return = get_returns(fund)
    bench_return = get_returns(benchmark)
    treas_return = treasury['Close'][-1]

    alpha_val = fund_return - treas_return - \
        beta * (bench_return - treas_return)
    print(f"alpha: {alpha_val}, beta: {beta}")

    alpha['value'] = alpha_val
    alpha['returns'] = {'fund': fund_return,
                        'benchmark': bench_return, 'treasury': treas_return}

    return alpha


def get_returns(data: pd.DataFrame, output='annual') -> float:

    # Determine intervals for returns, start with annual
    years = 1
    quarters = 4
    if len(data['Close']) > 300:
        years = 2
        quarters = 8
    if len(data['Close']) > 550:
        years = 5
        quarters = 20
    if len(data['Close']) > 1500:
        years = 10
        quarters = 40

    annual_returns = 0.0
    for i in range(years):
        annual_returns += (data['Adj Close'][(i+1)*250] - data['Adj Close']
                           [i * 250]) / data['Adj Close'][i * 250] * 100.0

    annual_returns /= float(years)

    # Determine intervals for returns, next with quarterly
    q_returns = 0.0
    counter = 0
    for i in range(quarters):
        multiple = 62
        if i % 2 != 0:
            multiple = 63
        counter += multiple

        q_returns += (data['Adj Close'][counter] - data['Adj Close']
                      [counter - multiple]) / data['Adj Close'][counter - multiple] * 100.0

    q_returns /= float(quarters)
    q_returns *= 4.0

    returns = np.mean([q_returns, annual_returns])
    if output == 'quarterly':
        returns /= 4.0

    return returns
