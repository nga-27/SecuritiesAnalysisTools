""" ledger """
import os
import datetime
import glob
from typing import Union

import pandas as pd
import numpy as np

from libs.utils import download_data, PlotType, generate_plot
from libs.tools.metadata_tools.dividends import get_dividends


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
    generate_plot(
        PlotType.GENERIC_PLOTTING, plots['prices'], **dict(
            title="Custom Funds", ylabel='Price', legend=plots['tickers'], x=plots['x']
        )
    )

    export_funds(ledgers)


def extract_from_format(ledger: pd.DataFrame, index: int = 0) -> dict:
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
    if ledger['Unnamed: 1'][2] != 'NaN':
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


def find_start_index(ledger: pd.DataFrame, column_name: str) -> Union[int, None]:
    """Find Start Index

    Arguments:
        ledger {pd.DataFrame} -- ledger file content
        title {str} -- column name in ledger

    Returns:
        int -- index of start of actual ledger content
    """
    key = 'Stock'
    max_threshold = 1000
    for i, row in enumerate(ledger[column_name]):
        if row == key:
            return i + 1
        if i > max_threshold:
            print(
                f"ERROR: Badly formed ledger file. No keyword '{key}' in correct location.")
            return None
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
        if ticker not in funds and '_' not in ticker:
            funds.append(ticker)

    return funds, new_ledger


def create_fund(content: dict) -> dict:
    """Create Fund

    Arguments:
        content {dict} -- data object with all fund data

    Returns:
        dict -- updates content with actual fund
    """
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    ledger = content['ledger']
    data = content['raw']

    temp_tick = ledger['Stock'][0]
    max_threshold = 100
    i = 0
    while i < max_threshold:
        if temp_tick in data:
            break
        i += 1
        temp_tick = ledger['Stock'][i]

    composite = {
        '_cash_': {
            'value': [float(content['start_capital'])] * len(data[temp_tick]['Close'])
        }
    }

    full_dates = data[temp_tick].index

    for i, ticker in enumerate(ledger['Stock']):
        if '_' in ticker:
            action = ledger['Action'][i]

            date = date_converter(ledger['Date'][i])
            idx = 0
            for a_val, ind in enumerate(full_dates):
                if ind == date:
                    idx = a_val
                    break

            if action == 'Deposit':
                action = 'Sell'
            if action == 'Withdraw':
                action = 'Buy'

            if action == 'Buy':
                composite['_cash_']['value'][idx] -= float(ledger['Shares'][i]) * \
                    float(ledger['Price of Action'][i])
            if action == 'Sell':
                composite['_cash_']['value'][idx] += float(ledger['Shares'][i]) * \
                    float(ledger['Price of Action'][i])
            continue

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
        for _, value in composite.items():
            val += value['value'][i]
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

    content['dividends'] = generate_dividends(content)

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


def date_to_index(date, content: dict, try_again=False) -> int:
    """Date to Index

    Returns index of the stock dataset that the 'date' refers to. If try_again is True
    and the date is not exactly in the dataset (e.g. a weekend, holiday), it will find
    the next later applicable date. A true match will exist if try_again is false.

    Arguments:
        date {str, datetime} -- date to match
        content {dict} -- fund ticker data object (entirety)

    Keyword Arguments:
        try_again {bool} -- true to find nearest neighbor on a match miss (default: {False})

    Returns:
        int -- index of match (or nearest if try_again=True)
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d")

    data = content['raw']
    temp_tick = list(data.keys())[0]
    date_list = data[temp_tick].index

    idx = None
    for a_val, date_x in enumerate(date_list):
        if date == date_x:
            idx = a_val
            break

        if try_again:
            if date <= date_x:
                idx = a_val
                break
    return idx


def generate_dividends(content: dict) -> dict:
    """Generate Dividends

    Uses yfinance api to pull dividends of stocks, this function then
    generates the new 'fund' dividends using applicable rules.

    Arguments:
        content {dict} -- new 'fund' data object

    Returns:
        dict -- dividend data object
    """
    # pylint: disable=too-many-locals,too-many-branches
    divs = {'raw': {}, 'refined': {'dates': [], 'dividends': []}}
    data = content['raw']

    temp_tick = list(data.keys())[0]
    start_date = data[temp_tick].index[0]

    print("Fetching Dividends...")
    # pylint: disable=too-many-nested-blocks
    for ticker in data:
        if ticker != '^GSPC':
            divs['raw'][ticker] = get_dividends(None, symbol=ticker)

            if len(divs['raw'][ticker]['dates']) > 0:
                fund = content['details'][ticker]
                first_index = None

                for i, date in enumerate(divs['raw'][ticker]['dates']):
                    date_time = datetime.datetime.strptime(date, "%Y-%m-%d")
                    if date_time >= start_date:
                        first_index = i
                        break

                if first_index is not None:
                    for i in range(first_index, len(divs['raw'][ticker]['dates'])):
                        date = datetime.datetime.strptime(
                            divs['raw'][ticker]['dates'][i], "%Y-%m-%d")
                        idx = date_to_index(date, content)

                        if fund['shares'][idx] > 0.0:
                            divs['refined']['dates'].append(date)
                            amt = fund['shares'][idx] * \
                                divs['raw'][ticker]['dividends'][i]
                            divs['refined']['dividends'].append(amt)

    quarters = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]
    divs['actual'] = {}

    for i, date in enumerate(divs['refined']['dates']):
        year = str(date.year)
        if year not in divs['actual']:
            divs['actual'][year] = [{"value": 0.0}, {
                "value": 0.0}, {"value": 0.0}, {"value": 0.0}]

        month = date.month
        for j, qtr in enumerate(quarters):
            if month in qtr:
                divs['actual'][year][j]['value'] += np.round(
                    divs['refined']['dividends'][i], 2)

    for year in divs['actual']:
        for i, qtr in enumerate(divs['actual'][year]):
            month = max(quarters[i])
            day = 27
            date = f"{year}-{month}-{day}"
            index = date_to_index(date, content, try_again=True)

            if index is not None:
                ratio = qtr['value'] / content['tabular'][index]
                _yield = np.round(ratio * 400.0, 2)
                price = np.round(ratio * content['price'][index], 3)

                divs['actual'][year][i]['price'] = f"${price}"
                divs['actual'][year][i]['yield'] = f"{_yield}%"

    return divs


def create_plot_content(dataset: dict) -> dict:
    """Create Plot Content

    Consolidate plots and data content to make it easy to plot

    Arguments:
        dataset {dict} -- entire dataset of all created funds

    Returns:
        dict -- plot content for plotting
    """
    plot_content = {}

    plots = []
    tickers = []
    x_val = []
    for ticker in dataset:
        bench_mark = dataset[ticker]['bench']
        plots.append(dataset[ticker]['price'])
        tickers.append(dataset[ticker]['symbol'])
        x_val.append(list(dataset[ticker]['raw']['^GSPC'].index))

        plots.append(bench_mark)
        x_val.append(x_val[-1])
        tickers.append(f"S&P 500 - {tickers[-1]}")

    plot_content['x'] = x_val
    plot_content['prices'] = plots
    plot_content['tickers'] = tickers

    return plot_content


def export_funds(dataset: dict):
    """Export Funds

    Export generated content to .csv

    Arguments:
        dataset {dict} -- entire dataset of funds
    """
    out_dir = os.path.join("output", "custom")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for ticker in dataset:
        filename = ticker + ".csv"
        filepath = os.path.join(out_dir, filename)

        content = {'date': [], 'price': [],
                   'benchmark': [], 'holdings': [], 'percent': [], 'total': []}
        content['date'] = dataset[ticker]['raw']['^GSPC'].index
        content['price'] = dataset[ticker]['price']
        content['benchmark'] = dataset[ticker]['bench']

        holdings, percent, total = holdings_calculation(dataset[ticker])
        content['holdings'] = holdings
        content['percent'] = percent
        content['total'] = total

        for _ in range(len(content['holdings']), len(content['price'])):
            content['holdings'].append("")
            content['percent'].append("")
            content['total'].append("")

        content['dividend period'] = []
        content['dividend amount'] = []
        content['dividend yield'] = []

        dividends = dataset[ticker]['dividends']['actual']
        for year in dividends:
            for i, qtr in enumerate(dividends[year]):
                period = f"{year}-Q{i+1}"
                content['dividend period'].append(period)
                content['dividend amount'].append(qtr.get('price', ""))
                content['dividend yield'].append(qtr.get('yield', ""))

        for _ in range(len(content['dividend yield']), len(content['price'])):
            content['dividend period'].append("")
            content['dividend amount'].append("")
            content['dividend yield'].append("")

        data_frame = pd.DataFrame.from_dict(content)
        data_frame = data_frame.set_index('date')

        data_frame.to_csv(filepath)


def holdings_calculation(fund: dict) -> list:
    """Holdings Calculation

    Arguments:
        fund {dict} -- subset of entire ledger dict, specific to a custom fund

    Returns:
        list -- holdings, percent for each holding
    """
    holdings = []
    percent = []
    total = []

    total_value = fund['tabular'][-1]

    for stock in fund['details']:
        if stock == '_cash_':
            holdings.append("Cash")
        else:
            holdings.append(stock)

        value = np.round(fund['details'][stock]['value']
                         [-1] / total_value * 100.0, 2)
        percent.append(value)
        total.append(np.round(fund['details'][stock]['value'][-1], 2))

    zipped = list(zip(holdings, percent, total))
    zipped = sorted(zipped, key=lambda x: x[1], reverse=True)
    split = list(zip(*zipped))

    holdings = list(split[0])
    percent = list(split[1])
    total = list(split[2])

    return holdings, percent, total
