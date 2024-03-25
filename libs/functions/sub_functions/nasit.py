""" NASIT Functions """
import json
import os
from typing import Tuple

import pandas as pd
import numpy as np

from libs.utils import generate_plot, PlotType
from libs.nasit.ledger import generate_fund_from_ledger

from .utils import (
    function_data_download, TICKER, NORMAL, WARNING, UP_COLOR, DOWN_COLOR
)


def nasit_get_data(data: dict, config: dict) -> Tuple[dict, bool]:
    """nasit_get_data

    Args:
        data (dict): NASIT fund content that controls setting of NASIT funds
        config (dict): configuration dictionary

    Returns:
        _type_: _description_
    """
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
    """nasit_extraction

    Args:
        data (dict): NASIT config data
        ticker_data (list): NASIT ticker data
        has_cash (bool, optional): A cash fund, sometimes present in NASIT. Defaults to False.
        by_price (bool, optional): If True, then use 'Close'. Else 'Adj Close'. Defaults to True.

    Returns:
        _type_: _description_
    """
    subs = data.get('makeup', [])
    fund = nasit_build(ticker_data, subs, has_cash=has_cash, by_price=by_price)
    print(
        f"NASIT generation of {TICKER}{data.get('ticker')}{NORMAL} complete.")
    print("")
    return fund


def nasit_build(data: dict, makeup: dict, has_cash=False, by_price=True) -> list:
    """nasit_build

    Args:
        data (dict): NASIT ticker data
        makeup (dict): NASIT configuration data
        has_cash (bool, optional): True if a cash fund. Defaults to False.
        by_price (bool, optional): True if 'Close', else 'Adj Close'. Defaults to True.

    Returns:
        list: The new price of a particular NASIT fund
    """
    # pylint: disable=too-many-locals,invalid-name
    CASH_PERCENT = 0.01
    START_VALUE = 25.0
    deltas = {}
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
            diff = (data[tick][key][i] - data[tick][key][i-1]) / data[tick][key][i-1]
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
    """NASIT Generation Function

    Args:
        config (dict): configuration dictionary
        print_only (bool, optional): True if render in terminal, False for plots. Defaults to False.
    """
    # pylint: disable=too-many-locals
    print("Generating NASIT funds...")
    print("")
    nasit_file = 'nasit.json'
    if not os.path.exists(nasit_file):
        print(
            f"{WARNING}WARNING: 'nasit.json' not found. Exiting...{NORMAL}")
        return

    with open(nasit_file, 'r', encoding='utf-8') as n_file:
        nasit = json.load(n_file)

        fund_list = nasit.get('Funds', [])
        nasit_funds = {}
        for fund in fund_list:
            t_data, has_cash = nasit_get_data(fund, config)
            nasit_funds[fund.get('ticker')] = nasit_extraction(
                fund, t_data, has_cash=has_cash)
            nasit_funds[f"{fund.get('ticker')}_ret"] = nasit_extraction(
                fund, t_data, has_cash=has_cash, by_price=False)

        if print_only:
            for fund_name, fund_data in nasit_funds.items():
                if "_ret" not in fund_name:
                    fund = fund_name
                    price = np.round(fund_data[-1], 2)
                    change = np.round(price - fund_data[-2], 2)
                    change_price = np.round(
                        (price - fund_data[-2]) / fund_data[-2] * 100.0, 3)

                    if change > 0.0:
                        color = UP_COLOR
                    elif change < 0.0:
                        color = DOWN_COLOR
                    else:
                        color = NORMAL

                    print("")
                    print(
                        f"{TICKER}{fund}{color}   ${price} (${change}, {change_price}%){NORMAL}")
            print("")
            print("")
            return

        data_frame = pd.DataFrame(nasit_funds)
        out_file = 'output/NASIT.csv'
        data_frame.to_csv(out_file)

        plot_able = []
        plot_able2 = []
        names = []
        names2 = []

        for fund_name, fund_data in nasit_funds.items():
            if '_ret' not in fund_name:
                plot_able.append(fund_data)
                names.append(fund_name)
            else:
                plot_able2.append(fund_data)
                names2.append(fund_name)

        generate_plot(
            PlotType.GENERIC_PLOTTING, plot_able, **{
                "legend": names, "title": 'NASIT Passives'
            }
        )
        generate_plot(
            PlotType.GENERIC_PLOTTING, plot_able2, **{
                "legend": names2, "title": 'NASIT Passives [Returns]'
            }
        )

def ledger_function(config: dict):
    """ledger_function

    Args:
        config (dict): configuration dictionary
    """
    generate_fund_from_ledger(config['tickers'])
