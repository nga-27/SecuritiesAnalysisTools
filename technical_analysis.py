import pandas as pd 
import numpy as np 
import pprint 

import fix_yahoo_finance as yf 

from libs.tools import full_stochastic, ultimate_oscillator, cluster_oscs, RSI
from libs.tools import relative_strength, triple_moving_average
from libs.features import feature_head_and_shoulders

from libs.tools import get_trend_analysis, mov_avg_convergence_divergence, on_balance_volume
from libs.utils import name_parser, fund_list_extractor, index_extractor, index_appender
from libs.utils import configure_temp_dir, remove_temp_dir
from libs.metrics import nasit_composite_index

from libs.utils import ProgressBar
from libs.outputs import slide_creator

# https://stockcharts.com/school/doku.php?id=chart_school:overview:john_murphy_charting_made_easy

PROCESS_STEPS = 8


# DO NOT INCLUDE ^GSPC IN 'tickers' STRING
tickers = 'PFE'
tickers = index_appender(tickers)
sp500_index = index_extractor(tickers)

configure_temp_dir()

data = yf.download(tickers=tickers, period='1y', interval='1d', group_by='ticker')
funds = fund_list_extractor(data)

# Start of automated process
analysis = {}

for fund_name in funds:

    name = fund_name
    analysis[name] = {}

    p = ProgressBar(PROCESS_STEPS, name=name)
    p.start()

    print(fund_name)
    fund = data[fund_name]
    p.uptick()
    fundB = fund #pd.read_csv(fileB)
    p.uptick()

    analysis[name]['dates_covered'] = {'start': str(fund.index[0]), 'end': str(fund.index[len(fund['Close'])-1])}
    analysis[name]['name'] = name

    #full_stochastic(fund, name=name)

    #chart, dat = cluster_oscs(fund, function='full_stochastic', filter_thresh=3, name=name) 
    #analysis['full_stochastic'] = dat
    #chart, dat = cluster_oscs(fund, function='ultimate', filter_thresh=3, name=name)
    #analysis['ultimate'] = dat  
    #chart, dat = cluster_oscs(fund, function='rsi', filter_thresh=3, name=name)
    #analysis['rsi'] = dat
    chart, dat = cluster_oscs(fund, function='all', filter_thresh=3, name=name, plot_output=True)
    analysis[name]['weighted'] = dat
    p.uptick()

    on_balance_volume(fund, plot_output=True, name=name) 
    p.uptick()

    triple_moving_average(fund, plot_output=True, name=name)
    p.uptick()

    #analysis['rsi'] = RSI(fund, name=name)
    #analysis['ultimate'] = ultimate_oscillator(fund, name=name)

    analysis[name]['macd'] = mov_avg_convergence_divergence(fund, plot_output=True, name=name)
    p.uptick()

    #print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[50, 25, 12]))
    #print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[200, 50, 25]))

    analysis[name]['relative_strength'] = relative_strength(fund_name, fund_name, tickers=data, sector='', plot_output=True)
    analysis[name]['features'] = {}

    p.uptick()

    hs, ma = feature_head_and_shoulders(fund)
    analysis[name]['features']['head_shoulders'] = hs
    p.uptick()

    #print("")
    #print("")
    #print(f"{name} for {fund['Date'][len(fund['Date'])-1]}")
    #print("")
    #pprint.pprint(analysis['features'])
    #pprint.pprint(analysis['macd'])

slide_creator('2019', analysis)

remove_temp_dir()
print('Done.')
