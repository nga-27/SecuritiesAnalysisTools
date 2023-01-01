import os
import json
from typing import Tuple

from datetime import datetime
from dateutil.relativedelta import relativedelta

import yfinance as yf
import pandas as pd
import numpy as np

from intellistop import IntelliStop

import libs.utils.stable_yf as styf

from .data import download_single_fund, download_data_indexes
from .constants import STANDARD_COLORS, INDEXES, PRINT_CONSTANTS
from .plotting import generic_plotting

"""
    Utilizes advanced api calls of 'yfinance==0.1.50' as of 2019-11-21
    Obtains "Volatility Quotient" (VQ) from Tradestops.com
"""

WARNING = STANDARD_COLORS["warning"]
FUND = STANDARD_COLORS["ticker"]
NORMAL = STANDARD_COLORS["normal"]

REVERSE_LINE = PRINT_CONSTANTS["return_same_line"]


def get_api_metadata(fund_ticker: str, **kwargs) -> dict:
    """Get API Metadata

    Arguments:
        fund_ticker {str} -- fund name

    Optional Args:
        progress_bar {ProgressBar} -- (default: {None})
        max_close {float} -- max close for a period, for VQ (default: {None})
        data {pd.DataFrame} -- dataset, primarily for VQ (default: {None})
        plot_output {bool} -- 'Ratings by Firms' (default: {False})
        function {str} -- specific metadata functions (default: {'all'})

    Returns:
        dict -- contains all financial metadata available
    """
    pb = kwargs.get('progress_bar', None)
    plot_output = kwargs.get('plot_output', False)
    function = kwargs.get('function', 'all')

    fund_ticker_cleansed = INDEXES.get(fund_ticker, fund_ticker)
    api_print = f"\r\nFetching API metadata for {FUND}{fund_ticker_cleansed}{NORMAL}..."
    print(api_print)

    metadata = {}
    ticker = yf.Ticker(fund_ticker)
    if pb is not None:
        pb.uptick(increment=0.2)

    st_tick = styf.Ticker(fund_ticker)
    if pb is not None:
        pb.uptick(increment=0.3)

    if function == 'all':
        metadata['dividends'] = AVAILABLE_KEYS.get('dividends')(ticker)

    if function == 'all' or function == 'info':
        metadata['info'] = AVAILABLE_KEYS.get('info')(ticker, st_tick, force_holdings=False)

    if function == 'all' or function == 'volatility':
        metadata['volatility'] = get_volatility(fund_ticker)
        if pb is not None:
            pb.uptick(increment=0.1)

    if ticker.info.get('holdings') or fund_ticker in INDEXES:
        # ETFs, Mutual Funds, and other indexes will have these but will output an ugly print
        # on financial data below, so let's just return what we have now.
        api_print += "  Canceled. (Fund is a mutual fund, ETF, or index.)"
        print(f"{REVERSE_LINE}{REVERSE_LINE}{REVERSE_LINE}{api_print}")
        return metadata

    if pb is not None:
        pb.uptick(increment=0.2)

    if function == 'all' or function == 'financials':
        metadata['financials'] = AVAILABLE_KEYS.get(
            'financials')(ticker, st_tick)

    if function == 'all' or function == 'balance':
        metadata['balance_sheet'] = AVAILABLE_KEYS.get(
            'balance')(ticker, st_tick)

    if pb is not None:
        pb.uptick(increment=0.1)

    if function == 'all':
        metadata['cashflow'] = AVAILABLE_KEYS.get('cashflow')(ticker, st_tick)
        metadata['earnings'] = AVAILABLE_KEYS.get('earnings')(ticker, st_tick)

    if function == 'all' or function == 'recommendations':
        metadata['recommendations'] = AVAILABLE_KEYS.get(
            'recommendations')(ticker, st_tick)

        metadata['recommendations']['tabular'] = calculate_recommendation_curve(
            metadata['recommendations'], plot_output=plot_output, name=fund_ticker)

    if function == 'all':
        # EPS needs some other figures to make it correct, but ok for now.
        metadata['eps'] = calculate_eps(metadata)
        if pb is not None:
            pb.uptick(increment=0.1)

    if function == 'all':
        metadata['altman_z'] = AVAILABLE_KEYS.get('altman_z')(metadata)

    api_print += "  Done."
    print(f"{REVERSE_LINE}{REVERSE_LINE}{REVERSE_LINE}{api_print}")

    return metadata


def get_dividends(ticker, symbol=None):
    """Get Dividends

    Will run yfinance API if ticker is None and symbol is not None 

    Arguments:
        ticker {yf-object} -- ticker object from yfinance

    Keyword Arguments:
        symbol {str} -- ticker symbol (default: {None})

    Returns:
        dict -- dividend data object
    """
    div = dict()
    if ticker is None and symbol is not None:
        ticker = yf.Ticker(symbol)

    try:
        t = ticker.dividends
        div['dates'] = [date.strftime("%Y-%m-%d") for date in t.keys()]
        div['dividends'] = [t[date] for date in t.keys()]
    except:
        div['dividends'] = []
        div['dates'] = []
    return div


def get_info(ticker, st, force_holdings=False):
    """Get Info

    Arguments:
        ticker {yf-object} -- ticker object from yfinance
        st {yf-object} -- ticker object from yfinance (0.1.50)

    Keyword Arguments:
        force_holdings {bool} -- only try old version (default: {False})

    Returns:
        dict -- fund info data object
    """
    if force_holdings:
        try:
            info = st.info
        except:
            info = dict()
    else:
        try:
            info = ticker.info
        except:
            try:
                info = st.info
            except:
                info = dict()
    return info


def get_financials(ticker, st):
    """Get Financials

    Arguments:
        ticker {yf-object} -- yfinance data object
        st {yf-object} -- ticker object from yfinance (0.1.50)

    Returns:
        dict -- finance data object
    """
    try:
        t = ticker.income_stmt
        fin = {index: list(row) for index, row in t.iterrows()}
        fin['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]

    except:
        fin = {}

    return fin


def get_balance_sheet(ticker, st):
    """Get Balance Sheet

    Arguments:
        ticker {yf-object} -- yfinance data object
        st {yf-object} -- ticker object from yfinance (0.1.50)

    Returns:
        dict -- Balance Sheet data object
    """
    try:
        t = ticker.balance_sheet
        bal = {index: list(row) for index, row in t.iterrows()}
        bal['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]

    except:
        bal = {}

    return bal


def get_cashflow(ticker, st):
    """Get Cashflow

    Arguments:
        ticker {yf-object} -- yfinance data object
        st {yf-object} -- ticker object from yfinance (0.1.50)

    Returns:
        dict -- Cashflow data object
    """
    try:
        t = ticker.cashflow
        cash = {index: list(row) for index, row in t.iterrows()}
        cash['dates'] = [col.strftime('%Y-%m-%d') for col in t.columns]

    except:
        cash = {}

    return cash


def get_earnings(ticker, st):
    """Get Earnings

    Arguments:
        ticker {yf-object} -- yfinance data object
        st {yf-object} -- ticker object from yfinance (0.1.50)

    Returns:
        dict -- Earnings data object
    """
    earn = {}

    try:
        t = ticker.earnings
        ey = {}
        ey['period'] = list(t.index)
        ey['revenue'] = [r for r in t['Revenue']]
        ey['earnings'] = [e for e in t['Earnings']]
        earn['yearly'] = ey
        q = ticker.quarterly_earnings
        eq = {}
        eq['period'] = list(q.index)
        eq['revenue'] = [r for r in q['Revenue']]
        eq['earnings'] = [e for e in t['Earnings']]
        earn['quarterly'] = eq

    except:
        earn['yearly'] = {}
        earn['quarterly'] = {}

    return earn


def get_recommendations(ticker, st) -> dict:
    """Get Recommendations

    Arguments:
        ticker {yf-object} -- current yf Ticker object
        st {yf-object} -- ticker object from yfinance (0.1.50)

    Returns:
        dict -- Recommendations data object
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


def get_altman_z_score(meta: dict) -> dict:
    """Get Altman Z-Score

    Created by Prof. Edward Altman (1968), info here: 
    https://www.investopedia.com/terms/a/altman.asp

    Each "letter" or term (A-E) represents a different aspect of a company's balance sheet:
        A: Liquidity
        B: Accumulated profits vs. assets
        C: How much profits the assets are producing
        D: Company's value vs. its liabilities
        E: Efficiency ratio (how much sales are generated from assets)

    Arguments:
        meta {dict} -- metadata object

    Returns:
        dict -- altman_z_score object
    """
    GOOD_THRESHOLD = 3.0
    BAD_THRESHOLD = 1.8

    balance_sheet = meta.get('balance_sheet')
    financials = meta.get('financials')
    info = meta.get('info')
    if balance_sheet is None or financials is None or info is None:
        return {"score": "n/a", "values": {}}

    total_assets = balance_sheet.get("Total Assets")
    if total_assets is None:
        return {"score": "n/a", "values": {}}

    current_assets = balance_sheet.get("Total Current Assets")
    if current_assets is None:
        return {"score": "n/a", "values": {}}

    current_liabilities = balance_sheet.get("Total Current Liabilities")
    if current_liabilities is None:
        return {"score": "n/a", "values": {}}

    working_capital = current_assets[0] / current_liabilities[0]
    altman_a = working_capital / total_assets[0] * 1.2

    retained_earnings = balance_sheet.get("Retained Earnings")
    if retained_earnings is None:
        return {"score": "n/a", "values": {}}
    altman_b = 1.4 * (retained_earnings[0] / total_assets[0])

    ebit = financials.get("Ebit")
    if ebit is None:
        return {"score": "n/a", "values": {}}
    altman_c = 3.3 * (ebit[0] / total_assets[0])

    market_cap = info.get("marketCap")
    if market_cap is None:
        return {"score": "n/a", "values": {}}

    total_liabilities = balance_sheet.get("Total Liab")
    if total_liabilities is None:
        return {"score": "n/a", "values": {}}
    altman_d = 0.6 * market_cap / total_liabilities[0]

    total_revenue = financials.get("Total Revenue")
    if total_revenue is None:
        return {"score": "n/a", "values": {}}

    altman_e = total_revenue[0] / total_assets[0]
    altman = altman_a + altman_b + altman_c + altman_d + altman_e

    if altman >= GOOD_THRESHOLD:
        color = "green"
    elif altman > BAD_THRESHOLD:
        color = "yellow"
    else:
        color = "red"

    z_score = {
        "score": altman,
        "color": color,
        "values":
        {
            "A": altman_a,
            "B": altman_b,
            "C": altman_c,
            "D": altman_d,
            "E": altman_e
        }
    }

    return z_score


AVAILABLE_KEYS = {
    "dividends": get_dividends,
    "info": get_info,
    "financials": get_financials,
    "balance": get_balance_sheet,
    "cashflow": get_cashflow,
    "earnings": get_earnings,
    "recommendations": get_recommendations,
    "altman_z": get_altman_z_score
}


def calculate_recommendation_curve(recoms: dict, **kwargs) -> dict:
    """Calculate Recommendation Curve

    Arguments:
        recoms {dict} -- recommendation data object

    Returns:
        dict -- recommendation curve data object
    """
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')

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

        x = [datetime.strptime(date, "%Y-%m-%d")
             for date in tabular['dates']]

        if plot_output:
            generic_plotting([tabular['grades']], x=x, title="Ratings by Firms",
                             ylabel="Ratings (Proportional 0 - 4)")

        else:
            filename = os.path.join(name, f"grades_{name}.png")
            generic_plotting([tabular['grades']], x=x, title="Ratings by Firms",
                             ylabel="Ratings (Proportional 0 - 4)",
                             saveFig=True, filename=filename)

    return tabular


def grade_to_number(grades: list) -> list:
    """Grade to Number

    Arguments:
        grades {list} -- list of recommendation grades (strings)

    Returns:
        list -- list of grades (floats)
    """
    GRADES = {
        "Strong Buy": 4.0,
        "Buy": 3.0,
        "Overweight": 3.0,
        "Outperform": 3.0,
        "Neutral": 2.0,
        "Hold": 2.0,
        "Market Perform": 2.0,
        "Equal-Weight": 2.0,
        "Sector Perform": 2.0,
        "Underperform": 1.0,
        "Underweight": 1.0,
        "Sell": 0.0
    }

    val_grad = []
    for grade in grades:
        val_grad.append(GRADES.get(grade, 3.0))
    return val_grad


def prune_ratings(firms: dict, date: str) -> dict:
    """Prune Ratings

    To keep ratings fresh, eliminate old ratings (beyond 2 years from 'date')

    Arguments:
        firms {dict} -- firm data object (from recommendation curve)
        date {str} -- specific point in time to add 2 years to

    Returns:
        dict -- pruned firm list
    """
    td = datetime.strptime(date, '%Y-%m-%d')
    for firm in list(firms):
        td2 = datetime.strptime(firms[firm]['date'], '%Y-%m-%d')
        td2 = td2 + relativedelta(years=2)
        if td > td2:
            firms.pop(firm)

    return firms


def calculate_eps(meta: dict) -> dict:
    """Calculate Earnings Per Share

    Arguments:
        meta {dict} -- metadata object

    Returns:
        dict -- EPS data object
    """
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


def api_sector_match(sector: str, config: dict, fund_len=None, **kwargs) -> list:
    """API Sector Match

    Arguments:
        sector {str} -- sector from sectors.json
        config {dict} -- controlling configuration dictionary

    Keyword Arguments:
        fund_len {int} -- for downloading dataset (default: {None})

    Optional Args:
        period {str} -- different period than in config (default: {config['period']})
        interval {str} -- different interval than in config (default: {config['interval']})

    Returns:
        list -- matched list of sector funds, data for matched list
    """
    period = kwargs.get('period', config['period'])
    interval = kwargs.get('interval', config['interval'])

    sector_match_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(sector_match_file):
        print(f"{WARNING}Warning: sector file '{sector_match_file}' not found.{NORMAL}")
        return None, None

    with open(sector_match_file) as f:
        matcher = json.load(f)
        matched = matcher.get("Sector", {}).get(sector)
        if matched is None:
            return None, None

        # To save downloads, if the matched items are already in the ticker list, simply use them
        tickers = config.get('tickers', '').split(' ')
        if matched in tickers:
            return matched, {}

        fund_data = download_single_fund(
            matched, config, period=period, interval=interval, fund_len=fund_len)
        return matched, fund_data


def api_sector_funds(sector_fund: str, config: dict, fund_len=None, **kwargs) -> list:
    """API Sector Funds

    Arguments:
        sector {str} -- sector from sectors.json
        config {dict} -- controlling configuration dictionary

    Keyword Arguments:
        fund_len {int} -- for downloading dataset (default: {None})

    Optional Args:
        period {str} -- different period than in config (default: {'2y'})
        interval {str} -- different interval than in config (default: {'1d'})

    Returns:
        list -- [description]
    """
    period = kwargs.get('period', '2y')
    interval = kwargs.get('interval', '1d')

    sector_match_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(sector_match_file):
        print(
            f"{WARNING}Warning: sector file '{sector_match_file}' not found.{NORMAL}")
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
            indexes=matched, tickers=tickers, fund_len=fund_len, period=period, interval=interval)
        return matched, fund_data

#####################################################


def get_volatility(ticker_str: str) -> dict:
    """Get Volatility

    Arguments:
        ticker_str {str} -- ticker of fund

    Returns:
        dict -- volatility quotient data object
    """
    volatility_factor = {}
    ticker_str = ticker_str.upper()

    stops = IntelliStop()
    vf_data = stops.run_analysis_for_ticker(ticker_str)
    close = stops.return_data(ticker_str)

    volatility_factor = {
        "VF": np.round(vf_data.vf.curated, 3),
        "stop_loss": np.round(vf_data.stop_loss.curated, 2),
        "latest_price": close[-1],
        "last_max": {
            "Date": vf_data.current_status.max_price_date,
            "Price": np.round(vf_data.current_status.max_price, 2)
        },
        "stopped_out": "OK" if vf_data.current_status.status.value != "stopped_out" else "stopped_out"
    }

    if vf_data.current_status.status.value == "stopped_out":
        volatility_factor['stop_loss'] = 0.0
    
    status, color = volatility_factor_status_print(vf_data.current_status.status.value)
    volatility_factor['status'] = {'status': status, 'color': color}

    return volatility_factor


def volatility_factor_status_print(vf_data_status: str) -> Tuple[str, str]:
    """VF Status Print

    Arguments:
        vf_data_status {dict} -- volatility quotient data object
        fund {str} -- fund name

    Returns:
        Tuple[str, str] -- status message, status color
    """
    if vf_data_status == "stopped_out":
        status_color = 'red'
        status_message = "AVOID - Stopped Out"
    elif vf_data_status == "caution_zone":
        status_color = 'yellow'
        status_message = "CAUTION - Hold"
    else:
        status_color = 'green'
        status_message = "GOOD - Buy / Maintain"

    return status_message, status_color
