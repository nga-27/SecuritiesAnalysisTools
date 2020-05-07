import os
import datetime
import pandas as pd
import numpy as np

from libs.utils import download_data


def generate_fund_from_ledger(ledger_name: str):

    path = os.path.join("resources", "ledgers", ledger_name)
    if not os.path.exists(path):
        print(f"No ledger named '{path}' found.")
        return

    ledger = pd.read_csv(path)
    content = extract_from_format(ledger)
    print(content['ledger'])


def extract_from_format(ledger: pd.DataFrame) -> dict:

    content = {}
    content['title'] = ledger.columns[0]
    content['start_capital'] = ledger['Unnamed: 1'][1]
    content['start_index'] = find_start_index(ledger, content['title'])

    funds, new_ledger = extract_funds(
        ledger, content['start_index'], content['title'])
    content['funds'] = funds
    content['ledger'] = new_ledger
    content['start_date'] = new_ledger['Date'][content['start_index']]

    content['start_date'] = datetime.datetime.strptime(
        content['start_date'], "%m/%d/%Y").strftime("%Y-%m-%d")
    content['end_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    tickers = ' '.join(content['funds'])
    ticker_str = ', '.join(content['funds'])

    controller = {
        'start': content['start_date'],
        'end': content['end_date'],
        'tickers': tickers,
        'ticker print': ticker_str
    }

    data, _indexes = download_data(
        controller, start=content['start_date'], end=content['end_date'])

    content['raw'] = data

    return content


def find_start_index(ledger: pd.DataFrame, title: str) -> int:
    KEY = 'Stock'
    MAX = 1000
    for i, row in enumerate(ledger[title]):
        if row == KEY:
            return (i+1)
        if i > MAX:
            print(
                f"ERROR: Badly formed ledger file. No keyword '{KEY}' in correct location.")
            return None


def extract_funds(ledger: pd.DataFrame, start_index: int, title: str) -> list:
    new_columns = {col: ledger[col][start_index-1]
                   for col in ledger.columns}
    new_ledger = ledger.rename(columns=new_columns)
    new_ledger = new_ledger.drop(list(range(start_index)))
    print(f"\r\n\r\n{new_ledger}")

    funds = []
    for ticker in new_ledger['Stock']:
        if ticker not in funds:
            funds.append(ticker)

    return funds, new_ledger
