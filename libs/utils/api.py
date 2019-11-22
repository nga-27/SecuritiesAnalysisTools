import yfinance as yf 
import pandas as pd 
import numpy as np 

import libs.utils.stable_yf as styf

"""
    Utilizes advanced api calls of 'yfinance==0.1.50' as of 2019-11-21
"""

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
        info = st.info
    return info
        

AVAILABLE_KEYS = {
    "dividends": get_dividends,
    "info": get_info
}

def get_api_metadata(fund_ticker: str):
    metadata = {}
    ticker = yf.Ticker(fund_ticker)
    st_tick = styf.Ticker(fund_ticker)

    metadata['dividends'] = AVAILABLE_KEYS['dividends'](ticker)
    metadata['info'] = AVAILABLE_KEYS['info'](ticker, st_tick)

    return metadata