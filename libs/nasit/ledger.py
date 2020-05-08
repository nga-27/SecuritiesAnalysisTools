import os
import math
import datetime
import glob
import pandas as pd
import numpy as np

from libs.utils import download_data
from libs.utils import generic_plotting


def generate_fund_from_ledger(ledger_name: str):
    """Generate Fund from Ledger

    Arguments:
        ledger_name {str} -- either 'all' or a filename
    """
    if ledger_name == 'all' or ledger_name == 'all'.upper():
        path = os.path.join("resources", "ledgers")
        if not os.path.exists(path):
            print(f"No ledger directory '{path}' found.")
            return

        path = os.path.join(path, "*.csv")
        globs = glob.glob(path)

    else:
        path = os.path.join("resources", "ledgers", ledger_name)
        if not os.path.exists(path):
            print(f"No ledger named '{path}' found.")
            return

        globs = [path]

    ledgers = {}
    for i, path in enumerate(globs):
        ledger = pd.read_csv(path)
        content = extract_from_format(ledger, index=i)
        content = create_fund(content)

        ledgers[content['symbol']] = content

    plots = create_plot_content(ledgers)

    generic_plotting(plots['prices'],
                     title="Custom Funds",
                     ylabel='Price',
                     legend=plots['tickers'],
                     x=plots['x'])


def extract_from_format(ledger: pd.DataFrame, index=0) -> dict:
    """Extract from Format

    Arguments:
        ledger {pd.DataFrame} -- dataframe-converted csv of ledger file

    Keyword Arguments:
        index {int} -- to differentiate on 'ticker' (default: {0})

    Returns:
        dict -- content of ledger extracted
    """
    content = {}
    content['title'] = ledger.columns[0]
    content['start_capital'] = float(ledger['Unnamed: 1'][1])

    content['symbol'] = f"NGAxy-{index}"
    if not math.isnan(ledger['Unnamed: 1'][2]):
        content['symbol'] = ledger['Unnamed: 1'][2]

    content['start_index'] = find_start_index(ledger, content['title'])

    funds, new_ledger = extract_funds(
        ledger, content['start_index'])
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
        'tickers': tickers + ' ^GSPC',
        'ticker print': ticker_str + ', and S&P500'
    }

    data, _indexes = download_data(
        controller, start=content['start_date'], end=content['end_date'])

    content['raw'] = data

    return content


def find_start_index(ledger: pd.DataFrame, column_name: str) -> int:
    """Find Start Index

    Arguments:
        ledger {pd.DataFrame} -- ledger file content
        title {str} -- column name in ledger

    Returns:
        int -- index of start of actual ledger content
    """
    KEY = 'Stock'
    MAX = 1000
    for i, row in enumerate(ledger[column_name]):
        if row == KEY:
            return (i+1)
        if i > MAX:
            print(
                f"ERROR: Badly formed ledger file. No keyword '{KEY}' in correct location.")
            return None


def extract_funds(ledger: pd.DataFrame, start_index: int) -> list:
    """Extract Funds

    Arguments:
        ledger {pd.DataFrame} -- ledger content
        start_index {int} -- start index of actual fund data
        title {str} -- [description]

    Returns:
        list -- ticker list, cleansed ledger dataframe
    """
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
    """Create Fund

    Arguments:
        content {dict} -- data object with all fund data

    Returns:
        dict -- updates content with actual fund
    """
    ledger = content['ledger']
    data = content['raw']

    temp_tick = ledger['Stock'][0]
    composite = {
        '_cash_': {
            'value': [content['start_capital']] * len(data[temp_tick]['Close'])
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
    for i in range(len(data[temp_tick]['Close'])):
        val = 0.0
        for ticker in composite:
            val += composite[ticker]['value'][i]
        value.append(val)

    content['tabular'] = value

    start_price = 25.0
    price = [start_price]
    for i in range(1, len(data[temp_tick]['Close'])):
        prc = start_price * (content['tabular'][i] / content['start_capital'])
        price.append(prc)

    content['price'] = price

    bench = [start_price]
    if '^GSPC' in data:
        for i in range(1, len(data['^GSPC'])):
            prc = start_price * (data['^GSPC']['Close']
                                 [i] / data['^GSPC']['Close'][0])
            bench.append(prc)

    content['bench'] = bench

    return content


def date_converter(ledger_date: str, _type='date') -> str:
    """Date Converter

    Swaps date form to match that of either a string or dataframe date

    Arguments:
        ledger_date {str} -- string-based date from ledger file

    Keyword Arguments:
        _type {str} -- output type, either 'date' or 'str' (default: {'date'})

    Returns:
        str -- converted date, technically could be a datetime object too
    """
    if _type == 'date':
        new_date = datetime.datetime.strptime(
            ledger_date, "%m/%d/%Y")
    elif _type == 'str':
        new_date = datetime.datetime.strptime(
            ledger_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    return new_date


def create_plot_content(dataset: dict) -> dict:
    """Create Plot Content

    Consolidate plots and data content to make it easy to plot

    Arguments:
        dataset {dict} -- entire dataset of all created funds

    Returns:
        dict -- plot content for plotting
    """
    plot_content = dict()

    plots = []
    tickers = []
    for ticker in dataset:
        bench_mark = dataset[ticker]['bench']
        plots.append(dataset[ticker]['price'])
        tickers.append(dataset[ticker]['symbol'])
        x = dataset[ticker]['raw']['^GSPC'].index

    plots.append(bench_mark)
    tickers.append("S&P 500")

    plot_content['x'] = x
    plot_content['prices'] = plots
    plot_content['tickers'] = tickers

    return plot_content
