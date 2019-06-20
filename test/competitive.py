import pandas as pd 
import numpy as np 
import yfinance as yf

def test_competitive(ticker_set, analysis: dict, start_invest=100000):
    """ Compare technical traits on when to buy sell securities """

    test_analysis = {}

    ticks = list(analysis.keys())
    test_analysis['benchmark'] = init_benchmark(ticker_set, ticks, start_invest)
    print(test_analysis)

    return test_analysis 


#######################################################################################

def init_benchmark(ticker_set, tickers: list, invest_amt: int) -> dict:
    bench = {}

    for tick in tickers:
        bench[tick] = {}

        bench[tick]['init_amt'] = invest_amt
        shares, cash = init_shares(ticker_set, tick, invest_amt)
        bench[tick]['init_shares'] = shares
        bench[tick]['cash'] = cash

        bench = final_amount(ticker_set, tick, bench, ticker_set[tick]['Close'].index[0])

    return bench


def init_shares(ticker_set, ticker: str, invest_amt: int):
    sh_price = ticker_set[ticker]['Close'][0]
    shares = np.floor(float(invest_amt) / sh_price)
    cash = np.round(float(invest_amt) - (shares * sh_price), 2)
    return shares, cash


def final_amount(ticker_set, ticker: str, benchmark: dict, start_date) -> dict:
    data = yf.Ticker(ticker)
    dividends = data.dividends
    shares = benchmark[ticker]['init_shares']

    if len(dividends) > 0:
        start_index = 0
        while ((start_index < len(dividends)) and (start_date > dividends.index[start_index])):
            start_index += 1
        if start_index < len(dividends):
            # print(dividends.index[start_index])
            for index in range(start_index, len(dividends)):
                date = dividends.index[index]
                price = ticker_set[ticker]['Close'][date]
                div_price = dividends[index]
                shares = np.round(float(shares) * (div_price/price + 1.0), 3)

    benchmark[ticker]['final_shares'] = float(shares)
    final_price = ticker_set[ticker]['Close'][len(ticker_set[ticker]['Close'])-1]
    benchmark[ticker]['final_amt'] = np.round(final_price * benchmark[ticker]['final_shares'] + benchmark[ticker]['cash'], 2)

    return benchmark

    