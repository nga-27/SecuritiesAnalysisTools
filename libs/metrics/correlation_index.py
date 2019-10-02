import pandas as pd 
import numpy as np 
from datetime import datetime

from libs.utils import download_data_indexes, index_appender

def correlation_composite_index(config: dict):
    print("corr_comp_ind")
    data = metrics_initializer()
    print(f"data len {len(data['VGT'].index)}")


def metrics_initializer() -> dict:
    tickers = 'VGT VHT VCR VDC VFH VDE VIS VOX VNQ VPU VAW'
    # sectors = tickers.split(' ')
    tickers = index_appender(tickers)
    all_tickers = tickers.split(' ')
    date = datetime.now().strftime('%Y-%m-%d')
    print(f"date: {date}")
    print(" ")
    print('Fetching Correlation Composite Index funds...')
    data, _ = download_data_indexes(indexes=all_tickers, tickers=tickers, start='2005-01-01', end=date, interval='1d')
    print(" ")
    return data

def get_correlation(data: dict):
    PERIOD_LENGTH = 100