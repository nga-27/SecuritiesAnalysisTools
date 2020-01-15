import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import pprint
import requests

from datetime import datetime
from dateutil.relativedelta import relativedelta

import libs.utils.stable_yf as styf
from .progress_bar import ProgressBar
from .data import download_single_fund, download_data_indexes
from .constants import TEXT_COLOR_MAP

"""
    Utilizes advanced api calls of 'yfinance==0.1.50' as of 2019-11-21
    Obtains "Volatility Quotient" (VQ) from Tradestops.com
"""

VQ_API_BASE_URL = "https://sts.tradesmith.com/api/StsApiService/"
VQ_VALUES_PARAM = "get-sts-values/"
VQ_LOOKUP_PARAM = "search-symbol/"
VQ_DEEP_ANALYSIS_PARAM = "get-tmc-data/"

TRADESTOPS_URL = "https://tradestops.com/investment-calculator/"

WARN_COLOR = TEXT_COLOR_MAP["yellow"]
NORMAL_COLOR = TEXT_COLOR_MAP["white"]


def get_dividends(ticker):
    div = dict()
    try:
        t = ticker.dividends
        div['dates'] = [date.strftime("%Y-%m-%d") for date in t.keys()]
        div['dividends'] = [t[date] for date in t.keys()]
    except:
        div['dividends'] = []
        div['dates'] = []
    return div


def get_info(ticker, st):
    try:
        info = ticker.info
    except:
        try:
            info = st.info
        except:
            info = dict()
    return info


def get_financials(ticker, st):
    try:
        t = ticker.financials
        fin = {index: list(row) for index, row in t.iterrows()}
        fin['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
    except:
        try:
            t = st.financials
            fin = {index: list(row) for index, row in t.iterrows()}
            fin['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
        except:
            fin = dict()
    return fin


def get_balance_sheet(ticker, st):
    try:
        t = ticker.balance_sheet
        bal = {index: list(row) for index, row in t.iterrows()}
        bal['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
    except:
        try:
            t = st.balance_sheet
            bal = {index: list(row) for index, row in t.iterrows()}
            bal['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
        except:
            bal = dict()
    return bal


def get_cashflow(ticker, st):
    try:
        t = ticker.cashflow
        cash = {index: list(row) for index, row in t.iterrows()}
        cash['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
    except:
        try:
            t = st.balance_sheet
            cash = {index: list(row) for index, row in t.iterrows()}
            cash['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]
        except:
            cash = dict()
    return cash


def get_earnings(ticker, st):
    earn = dict()
    try:
        t = ticker.earnings
        ey = dict()
        ey['period'] = list(t.index)
        ey['revenue'] = [r for r in t['Revenue']]
        ey['earnings'] = [e for e in t['Earnings']]
        earn['yearly'] = ey
        q = ticker.quarterly_earnings
        eq = dict()
        eq['period'] = list(q.index)
        eq['revenue'] = [r for r in q['Revenue']]
        eq['earnings'] = [e for e in t['Earnings']]
        earn['quarterly'] = eq
    except:
        try:
            t = st.earnings
            ey = dict()
            ey['period'] = list(t.index)
            ey['revenue'] = [r for r in t['Revenue']]
            ey['earnings'] = [e for e in t['Earnings']]
            earn['yearly'] = ey
            q = st.quarterly_earnings
            eq = dict()
            eq['period'] = list(q.index)
            eq['revenue'] = [r for r in q['Revenue']]
            eq['earnings'] = [e for e in t['Earnings']]
            earn['quarterly'] = eq
        except:
            earn['yearly'] = {}
            earn['quarterly'] = {}
    return earn


def get_recommendations(ticker, st):
    """[summary]

    Arguments:
        ticker {[type]} -- [description]
        st {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    recom = dict()
    try:
        t = ticker.recommendations
        recom['dates'] = [date.strftime('%Y-%m-%d') for date in t.index]
        recom['firms'] = [f for f in t['Firm']]
        recom['grades'] = [g for g in t['To Grade']]
        recom['actions'] = [a for a in t['Action']]
    except:
        try:
            t = st.recommendations
            recom['dates'] = [date.strftime('%Y-%m-%d') for date in t.index]
            recom['firms'] = [f for f in t['Firm']]
            recom['grades'] = [g for g in t['To Grade']]
            recom['actions'] = [a for a in t['Action']]
        except:
            recom = {'dates': [], 'firms': [], 'grades': [], 'actions': []}
    return recom


AVAILABLE_KEYS = {
    "dividends": get_dividends,
    "info": get_info,
    "financials": get_financials,
    "balance": get_balance_sheet,
    "cashflow": get_cashflow,
    "earnings": get_earnings,
    "recommendations": get_recommendations
}


def get_api_metadata(fund_ticker: str, **kwargs) -> dict:
    """
    Get Api Metadata

    args:
        fund_ticker:    (str) fund name

    optional args:
        progress_bar:   (ProgressBar) DEFAULT=None

    returns:
        metadata:       (dict) contains all financial metadata available
    """
    pb = kwargs.get('progress_bar', None)
    max_close = kwargs.get('max_close', None)

    metadata = {}
    ticker = yf.Ticker(fund_ticker)
    if pb is not None:
        pb.uptick(increment=0.2)
    st_tick = styf.Ticker(fund_ticker)
    if pb is not None:
        pb.uptick(increment=0.3)

    metadata['dividends'] = AVAILABLE_KEYS.get('dividends')(ticker)
    metadata['info'] = AVAILABLE_KEYS.get('info')(ticker, st_tick)

    if pb is not None:
        pb.uptick(increment=0.2)

    metadata['financials'] = AVAILABLE_KEYS.get('financials')(ticker, st_tick)
    metadata['balance_sheet'] = AVAILABLE_KEYS.get('balance')(ticker, st_tick)

    if pb is not None:
        pb.uptick(increment=0.1)

    metadata['cashflow'] = AVAILABLE_KEYS.get('cashflow')(ticker, st_tick)
    metadata['earnings'] = AVAILABLE_KEYS.get('earnings')(ticker, st_tick)
    metadata['recommendations'] = AVAILABLE_KEYS.get(
        'recommendations')(ticker, st_tick)

    metadata['recommendations']['tabular'] = calculate_recommendation_curve(
        metadata['recommendations'])
    # EPS needs some other figures to make it correct, but ok for now.
    metadata['eps'] = calculate_eps(metadata)
    if pb is not None:
        pb.uptick(increment=0.1)

    metadata['volatility'] = get_volatility(fund_ticker, max_close=max_close)
    if pb is not None:
        pb.uptick(increment=0.1)

    return metadata


def calculate_recommendation_curve(recoms: dict) -> dict:
    tabular = dict()
    tabular['dates'] = []
    tabular['grades'] = []

    if len(recoms['dates']) > 0:
        firms = {}
        dates = []
        grades = []
        dates_x = recoms.get('dates', [])
        grades_x = grade_to_number(recoms.get('grades', []))
        firms_x = recoms.get('firms', [])

        i = 0
        while i < len(dates_x):
            date = dates_x[i]
            dates.append(date)
            while (i < len(dates_x)) and (date == dates_x[i]):
                firms[firms_x[i]] = {}
                firms[firms_x[i]]['grade'] = grades_x[i]
                firms[firms_x[i]]['date'] = date
                i += 1
            firms = prune_ratings(firms, date)
            sum_ = [firms[key]['grade'] for key in firms.keys()]
            grades.append(np.mean(sum_))

        tabular['grades'] = grades
        tabular['dates'] = dates

    return tabular


def grade_to_number(grades: list) -> list:
    GRADES = {
        "Strong Buy": 1.0,
        "Buy": 2.0,
        "Overweight": 2.0,
        "Outperform": 2.0,
        "Neutral": 3.0,
        "Hold": 3.0,
        "Market Perform": 3.0,
        "Equal-Weight": 3.0,
        "Sector Perform": 3.0,
        "Underperform": 4.0,
        "Underweight": 4.0,
        "Sell": 5.0
    }

    val_grad = []
    for grade in grades:
        val_grad.append(GRADES.get(grade, 3.0))
    return val_grad


def prune_ratings(firms: dict, date: str) -> dict:
    td = datetime.strptime(date, '%Y-%m-%d')
    for firm in list(firms):
        td2 = datetime.strptime(firms[firm]['date'], '%Y-%m-%d')
        td2 = td2 + relativedelta(years=2)
        if td > td2:
            firms.pop(firm)
    return firms


def calculate_eps(meta: dict) -> dict:
    eps = dict()
    q_earnings = meta.get('earnings', {}).get('quarterly', {})
    shares = meta.get('info', {}).get('sharesOutstanding')

    if shares and q_earnings:
        eps['period'] = []
        eps['eps'] = []
        for i, earn in enumerate(q_earnings['earnings']):
            eps['period'].append(q_earnings['period'][i])
            eps['eps'].append(np.round(earn / shares, 3))

    return eps


def api_sector_match(sector: str, config: dict, fund_len=None):
    sector_match_file = "resources/sectors.json"
    if not os.path.exists(sector_match_file):
        print(f"Warning: sector file '{sector_match_file}' not found.")
        return None, None

    with open(sector_match_file) as f:
        matcher = json.load(f)
        matched = matcher.get("Sector", {}).get(sector)
        if matched is None:
            return None, None

        tickers = config.get('tickers', '').split(' ')
        if matched in tickers:
            return matched, None
        fund_data = download_single_fund(matched, config, fund_len=fund_len)
        return matched, fund_data


def api_sector_funds(sector_fund: str, config: dict, fund_len=None):
    sector_match_file = "resources/sectors.json"
    if not os.path.exists(sector_match_file):
        print(
            f"{WARN_COLOR}Warning: sector file '{sector_match_file}' not found.{NORMAL_COLOR}")
        return [], {}

    if sector_fund is None:
        return [], {}
    with open(sector_match_file) as f:
        matcher = json.load(f)
        matched = matcher.get("Comparison", {}).get(sector_fund)
        if matched is None:
            return [], {}

        tickers = ' '.join(matched)
        fund_data, _ = download_data_indexes(
            indexes=matched, tickers=tickers, fund_len=fund_len)
        return matched, fund_data

#####################################################


def get_volatility(ticker_str: str, **kwargs):
    max_close = kwargs.get('max_close', None)
    is_SP500 = False
    vq = {}

    json_path = ''
    if os.path.exists('core.json'):
        json_path = 'core.json'
    elif os.path.exists('test.json'):
        json_path = 'test.json'

    if os.path.exists(json_path):
        with open(json_path) as json_file:
            core = json.load(json_file)
            key = core.get("Keys", {}).get("Volatility_Quotient", "")
            ticker_str = ticker_str.upper()

            if ticker_str == '^GSPC':
                ticker_str = 'SPY'
                is_SP500 = True

            url = f"{VQ_API_BASE_URL}{VQ_VALUES_PARAM}{key}/{ticker_str}"

            response = requests.get(url)
            r = response.json()
            if response.status_code != 200:
                print("")
                print(f"{WARN_COLOR}Volatility Quotient failed on {ticker_str} request: '{r.get('ErrorMessage', 'Failure.')}'. Check valid key.{NORMAL_COLOR}")
                print("")
                return vq

            vq = {"VQ": r.get("StsPercentValue", ""), "stop_loss": r.get(
                "StopPriceLong", ""), "latest_price": r.get("LatestClose")}
            vq['last_max'] = r.get('LastMax')
            if vq['last_max'] is None:
                vq['last_max'] = {"Date": "n/a", "Price": "n/a"}

            if is_SP500 and max_close is not None:
                vq['last_max'] = {"Date": "n/a", "Price": max_close}
                ratio = (100.0 - vq['VQ']) / 100.0
                vq['stop_loss'] = np.round(ratio * vq['last_max']['Price'], 2)

            url = f"{VQ_API_BASE_URL}{VQ_LOOKUP_PARAM}{key}/{ticker_str}/20"
            response = requests.get(url)
            r = response.json()
            if response.status_code == 200:
                val = None
                for tick in r.get('Symbols', []):
                    if tick['Symbol'] == ticker_str:
                        val = tick["SymbolId"]
                        break
                if val is not None:
                    now = datetime.now()
                    start = now - relativedelta(years=10)
                    start_str = start.strftime('%Y-%m-%d')
                    now_str = now.strftime('%Y-%m-%d')

                    url = f"{VQ_API_BASE_URL}{VQ_DEEP_ANALYSIS_PARAM}{key}/{val}/{start_str}/{now_str}"
                    response = requests.get(url)
                    r = response.json()
                    if response.status_code == 200:
                        vq['analysis'] = r

            return vq

    return vq
