import json
import os

import pandas as pd
import numpy as np

from libs.utils import generic_plotting
from libs.nasit import generate_fund_from_ledger

from .utils import (
    function_data_download, TICKER, NORMAL, WARNING, UP_COLOR, DOWN_COLOR
)


def nasit_get_data(data: dict, config: dict):
    subs = data.get('makeup', [])
    tickers = []
    has_cash = False
    for sub in subs:
        if sub['symbol'] != 'xCASHx':
            tickers.append(sub['symbol'])
        else:
            has_cash = True
    ticker_str = ' '.join(tickers)
    config['period'] = '2y'
    config['tickers'] = ticker_str
    config['ticker print'] = ', '.join(tickers)
    t_data, _ = function_data_download(config)
    return t_data, has_cash


def nasit_extraction(data: dict, ticker_data: list, has_cash=False, by_price=True):
    subs = data.get('makeup', [])
    fund = nasit_build(ticker_data, subs, has_cash=has_cash, by_price=by_price)
    print(
        f"NASIT generation of {TICKER}{data.get('ticker')}{NORMAL} complete.")
    print("")
    return fund


def nasit_build(data: dict, makeup: dict, has_cash=False, by_price=True):
    CASH_PERCENT = 0.01
    START_VALUE = 25.0
    deltas = dict()
    data_len = 0

    if by_price:
        key = 'Close'
    else:
        key = 'Adj Close'

    for tick in data:
        deltas[tick] = []
        deltas[tick].append(0.0)
        data_len = len(data[tick][key])
        for i in range(1, data_len):
            diff = (data[tick][key][i] - data[tick]
                    [key][i-1]) / data[tick][key][i-1]
            deltas[tick].append(diff)

    if has_cash:
        DIVISOR = CASH_PERCENT / float(data_len) / 2.0
        deltas['cash'] = [0.0]
        for i in range(1, data_len):
            deltas['cash'].append(DIVISOR)

    new_fund = [0.0] * data_len
    for component in makeup:
        sym = component['symbol']
        amt = component['allocation']
        if sym == 'xCASHx':
            sym = 'cash'
        for i, val in enumerate(deltas[sym]):
            new_fund[i] += val * amt

    new_closes = [START_VALUE]
    for i in range(1, len(new_fund)):
        close = new_closes[-1] * (1.0 + new_fund[i])
        new_closes.append(close)

    return new_closes

def nasit_generation_function(config: dict, print_only=False):
    print(f"Generating Nasit funds...")
    print(f"")
    nasit_file = 'nasit.json'
    if not os.path.exists(nasit_file):
        print(
            f"{WARNING}WARNING: 'nasit.json' not found. Exiting...{NORMAL}")
        return

    with open(nasit_file) as f:
        nasit = json.load(f)
        f.close()

        fund_list = nasit.get('Funds', [])
        nasit_funds = dict()
        for fund in fund_list:
            t_data, has_cash = nasit_get_data(fund, config)
            nasit_funds[fund.get('ticker')] = nasit_extraction(
                fund, t_data, has_cash=has_cash)
            nasit_funds[f"{fund.get('ticker')}_ret"] = nasit_extraction(
                fund, t_data, has_cash=has_cash, by_price=False)

        if print_only:
            for f in nasit_funds:
                if "_ret" not in f:
                    fund = f
                    price = np.round(nasit_funds[f][-1], 2)
                    change = np.round(price - nasit_funds[f][-2], 2)
                    changep = np.round(
                        (price - nasit_funds[f][-2]) / nasit_funds[f][-2] * 100.0, 3)

                    if change > 0.0:
                        color = UP_COLOR
                    elif change < 0.0:
                        color = DOWN_COLOR
                    else:
                        color = NORMAL

                    print("")
                    print(
                        f"{TICKER}{fund}{color}   ${price} (${change}, {changep}%){NORMAL}")
            print("")
            print("")
            return

        df = pd.DataFrame(nasit_funds)
        out_file = 'output/NASIT.csv'
        df.to_csv(out_file)

        plotable = []
        plotable2 = []
        names = []
        names2 = []

        for f in nasit_funds:
            if '_ret' not in f:
                plotable.append(nasit_funds[f])
                names.append(f)
            else:
                plotable2.append(nasit_funds[f])
                names2.append(f)

        generic_plotting(plotable, legend=names, title='NASIT Passives')
        generic_plotting(plotable2, legend=names2,
                         title='NASIT Passives [Returns]')


def ledger_function(config: dict):
    generate_fund_from_ledger(config['tickers'])
