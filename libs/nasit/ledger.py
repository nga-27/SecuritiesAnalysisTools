import os
import datetime
import pandas as pd
import numpy as np

from libs.utils import download_data
from libs.utils import generic_plotting


def generate_fund_from_ledger(ledger_name: str):

    path = os.path.join("resources", "ledgers", ledger_name)
    if not os.path.exists(path):
        print(f"No ledger named '{path}' found.")
        return

    ledger = pd.read_csv(path)
    content = extract_from_format(ledger)
    content = create_fund(content)

    generic_plotting([content['tabular']])


def extract_from_format(ledger: pd.DataFrame) -> dict:

    content = {}
    content['title'] = ledger.columns[0]
    content['start_capital'] = float(ledger['Unnamed: 1'][1])
    content['start_index'] = find_start_index(ledger, content['title'])

    funds, new_ledger = extract_funds(
        ledger, content['start_index'], content['title'])
    content['funds'] = funds
    content['ledger'] = new_ledger
    content['start_date'] = new_ledger['Date'][0]

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
    new_ledger.reset_index(inplace=True)

    funds = []
    for ticker in new_ledger['Stock']:
        if ticker not in funds:
            funds.append(ticker)

    return funds, new_ledger


def create_fund(content: dict) -> dict:
    ledger = content['ledger']
    data = content['raw']

    temp_tick = ledger['Stock'][0]
    composite = {
        '_cash_': {
            'value': [content['start_capital']] * len(data[temp_tick])
        }
    }

    for i, ticker in enumerate(ledger['Stock']):
        t_data = data[ticker]

        if ticker not in composite:
            composite[ticker] = {
                'value': [0.0] * len(t_data.index),
                'shares': [0] * len(t_data.index)
            }

        action = ledger['Action'][i]
        date = date_converter(ledger['Date'][i])

        for j, close in enumerate(t_data['Close']):

            if t_data.index[j] == date:
                if action == 'Buy':
                    composite[ticker]['shares'][j] += int(ledger['Shares'][i])
                    composite[ticker]['value'][j] += float(ledger['Shares'][i]) * \
                        float(ledger['Price of Action'][i])
                    composite['_cash_']['value'][j] -= float(ledger['Shares'][i]) * \
                        float(ledger['Price of Action'][i])

                elif action == 'Sell':
                    composite[ticker]['shares'][j] -= int(ledger['Shares'][i])
                    composite[ticker]['value'][j] -= float(ledger['Shares'][i]) * \
                        float(ledger['Price of Action'][i])
                    composite['_cash_']['value'][j] += float(ledger['Shares'][i]) * \
                        float(ledger['Price of Action'][i])

            else:
                if j > 0:
                    composite[ticker]['shares'][j] = composite[ticker]['shares'][j-1]
                    composite[ticker]['value'][j] = composite[ticker]['shares'][j] * close
                    composite['_cash_']['value'][j] = composite['_cash_']['value'][j-1]

    content['details'] = composite

    value = []
    for i in range(len(data[temp_tick])):
        val = 0.0
        for ticker in composite:
            val += composite[ticker]['value'][i]
        value.append(val)

    content['tabular'] = value

    return content


def date_converter(ledger_date: str, _type='date') -> str:
    if _type == 'date':
        new_date = datetime.datetime.strptime(
            ledger_date, "%m/%d/%Y")
    elif _type == 'str':
        new_date = datetime.datetime.strptime(
            ledger_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    return new_date
