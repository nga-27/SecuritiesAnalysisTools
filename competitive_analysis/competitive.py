import pandas as pd 
import numpy as np 
import yfinance as yf
import pprint
import copy

def test_competitive(ticker_set, analysis: dict, start_invest=100000):
    """ Compare technical traits on when to buy sell securities """

    test_analysis = {}

    ticks = list(analysis.keys())
    test_analysis['benchmark'] = init_benchmark(ticker_set, ticks, start_invest)
    test_analysis['cluster'] = run_clusters(ticker_set, ticks, analysis, start_invest)
    test_analysis = restructure_analysis(test_analysis)
    pprint.pprint(test_analysis)

    return test_analysis 


def restructure_analysis(test_analysis: dict) -> dict:
    bench = copy.deepcopy(test_analysis['benchmark'])
    cluster = copy.deepcopy(test_analysis['cluster'])

    new_analysis = dict()
    for key in bench.keys():
        new_analysis[key] = {}
        for k2 in bench[key].keys():
            k3 = f'bench_{k2}'
            new_analysis[key][k3] = bench[key][k2]
        for k2 in cluster[key].keys():
            k3 = f'cluster_{k2}'
            new_analysis[key][k3] = cluster[key][k2]

    return new_analysis

#######################################################################################

def run_clusters(ticker_set, tickers: list, analysis: dict, start_invest: int) -> dict:
    cluster = {}

    # Note: as trends are determined, THs will increase/decrease (rise=>SELL higher,BUY=> lower)
    SELL_TH = 0.6
    BUY_TH = 0.4
    SELL_AMT = 0.3
    BUY_AMT = 1.0
    ACCELERATOR = 1.2

    for tick in tickers:
        cluster[tick] = {}
        cluster[tick]['init_amt'] = start_invest
        shares, cash = init_shares(ticker_set, tick, start_invest)
        cluster[tick]['init_shares'] = shares
        cluster[tick]['cash'] = cash

        data = yf.Ticker(tick)
        dividends = data.dividends

        cluster_vals = []
        for clus in analysis[tick]['clustered_osc']['all']:
            cluster_vals.append(clus[2])
        sell = SELL_TH * np.max(cluster_vals)
        diff_s = np.max(cluster_vals) - sell
        buy = BUY_TH * np.min(cluster_vals)
        diff_b = np.min(cluster_vals) - buy
        print(f"clusters: {analysis[tick]['clustered_osc']['all'][0]}")
        print(f"tickers: {ticker_set[tick]['Close'][27]}")

        start_date = ticker_set[tick]['Close'].index[0]
        if len(dividends) > 0:
            start_index = 0
            while ((start_index < len(dividends)) and (start_date > dividends.index[start_index])):
                start_index += 1
            if start_index < len(dividends):
                print("dividend set here")

        for clus in analysis[tick]['clustered_osc']['all']:
            if clus[2] > sell:
                samt = SELL_AMT * (float(clus[2]) - sell) / diff_s
                sells = np.floor(float(shares) * samt)
                shares -= sells
                cash += np.round(float(sells) * clus[1], 2)
            if clus[2] < buy:
                bamt = BUY_AMT * (float(clus[2]) - buy) / diff_b * ACCELERATOR
                if bamt > 1.0:
                    bamt = 1.0
                b_cash = bamt * float(cash)
                shs = np.floor(b_cash / clus[1])
                cash = np.round(float(cash) - (float(shs) * clus[1]), 2)
                shares += shs 

        cluster[tick]['cash'] = cash
        cluster[tick]['final_shares'] = shares 
        final_price = ticker_set[tick]['Close'][len(ticker_set[tick]['Close'])-1]
        cluster[tick]['final_amt'] = np.round(final_price * cluster[tick]['final_shares'] + cluster[tick]['cash'], 2)

    return cluster


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

    