"""
release_1.py

Main release for milestone/release 1.
    > Technical analysis tools:
        > MACD
        > Clustered Oscillators
        > Moving Averages
        > Relative Strength (vs. S&P500)
        > Head & Shoulders feature detection
        > On-Balance Volume
    > Reporting outputs per security analyzed:
        > JSON with details
        > Powerpoint with plotting and summaries
    > Progress bar for analysis

Nick Amell
May 10, 2019
"""

import pandas as pd 
import numpy as np 
import pprint 

import fix_yahoo_finance as yf 

from libs.tools import full_stochastic, ultimate_oscillator, cluster_oscs, RSI
from libs.tools import relative_strength, triple_moving_average
from libs.features import feature_head_and_shoulders

from libs.tools import get_trend_analysis, mov_avg_convergence_divergence, on_balance_volume
from libs.utils import name_parser, fund_list_extractor, index_extractor, index_appender, date_extractor
from libs.utils import configure_temp_dir, remove_temp_dir, create_sub_temp_dir
from libs.metrics import nasit_composite_index

from libs.utils import ProgressBar
from libs.outputs import slide_creator, output_to_json
from libs.metrics import market_composite_index

PROCESS_STEPS = 8


# DO NOT INCLUDE ^GSPC IN 'tickers' STRING
tickers = 'VTI' # VHT VGT VOX VWO MMM VNQ VXUS VDC VWINX'
tickers = index_appender(tickers)
sp500_index = index_extractor(tickers)

remove_temp_dir()
configure_temp_dir()

data = yf.download(tickers=tickers, period='1y', interval='1d', group_by='ticker')
funds = fund_list_extractor(data)

# Start of automated process
analysis = {}

for fund_name in funds:

    name = fund_name
    
    create_sub_temp_dir(name)
    analysis[name] = {}

    p = ProgressBar(PROCESS_STEPS, name=name)
    p.start()

    fund = data[fund_name]
    p.uptick()
    fundB = fund #pd.read_csv(fileB)
    p.uptick()

    start = date_extractor(fund.index[0], _format='str')
    end = date_extractor(fund.index[len(fund['Close'])-1], _format='str')

    analysis[name]['dates_covered'] = {'start': str(start), 'end': str(end)} 
    analysis[name]['name'] = name

    chart, dat = cluster_oscs(fund, function='all', filter_thresh=3, name=name, plot_output=False)
    analysis[name]['clustered_osc'] = dat
    p.uptick()

    on_balance_volume(fund, plot_output=False, name=name)
    p.uptick()

    triple_moving_average(fund, plot_output=False, name=name)
    p.uptick()

    analysis[name]['macd'] = mov_avg_convergence_divergence(fund, plot_output=False, name=name)
    p.uptick()

    analysis[name]['relative_strength'] = relative_strength(fund_name, fund_name, tickers=data, sector='', plot_output=False)
    analysis[name]['features'] = {}

    p.uptick()

    hs, ma = feature_head_and_shoulders(fund)
    analysis[name]['features']['head_shoulders'] = hs
    p.uptick()


slide_creator('2019', analysis)
output_to_json(analysis)
#pprint.pprint(analysis)

market_composite_index()

#remove_temp_dir()
print('Done.')

