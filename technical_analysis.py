import pandas as pd 
import numpy as np 
import pprint 

import fix_yahoo_finance as yf 

from libs.tools import full_stochastic, ultimate_oscillator, cluster_oscs, RSI
from libs.tools import relative_strength, triple_moving_average
from libs.features import feature_head_and_shoulders

from libs.tools import get_trend_analysis, mov_avg_convergence_divergence, on_balance_volume
from libs.utils import name_parser, dir_lister, fund_list_extractor, index_extractor, index_appender
from libs.metrics import nasit_composite_index

from libs.utils import ProgressBar
from libs.outputs import slide_creator

# https://stockcharts.com/school/doku.php?id=chart_school:overview:john_murphy_charting_made_easy


# DO NOT INCLUDE ^GSPC IN 'tickers' STRING
tickers = 'VTI'
tickers = index_appender(tickers)
sp500_index = index_extractor(tickers)

data = yf.download(tickers=tickers, period='1y', interval='1d', group_by='ticker')
funds = fund_list_extractor(data)
#data = add_date_columns(data)

#sp500_index, files_to_parse = dir_lister()

#files_to_parse = [FILE]

for fund_name in funds:

    name = fund_name

    p = ProgressBar(8, name=name)
    p.start()

    print(fund_name)
    fund = data[fund_name]
    p.uptick()
    fundB = fund #pd.read_csv(fileB)
    p.uptick()

    # Start of automated process
    analysis = {}

    analysis['dates_covered'] = {'start': str(fund.index[0]), 'end': str(fund.index[len(fund['Close'])-1])}
    analysis['name'] = name

    #full_stochastic(fund, name=name)

    #chart, dat = cluster_oscs(fund, function='full_stochastic', filter_thresh=3, name=name) 
    #analysis['full_stochastic'] = dat
    #chart, dat = cluster_oscs(fund, function='ultimate', filter_thresh=3, name=name)
    #analysis['ultimate'] = dat  
    #chart, dat = cluster_oscs(fund, function='rsi', filter_thresh=3, name=name)
    #analysis['rsi'] = dat
    chart, dat = cluster_oscs(fund, function='all', filter_thresh=3, name=name, plot_output=True)
    analysis['weighted'] = dat
    p.uptick()

    on_balance_volume(fund, plotting=True)
    p.uptick()

    triple_moving_average(fund, plotting=True)
    p.uptick()

    #analysis['rsi'] = RSI(fund, name=name)
    #analysis['ultimate'] = ultimate_oscillator(fund, name=name)

    analysis['macd'] = mov_avg_convergence_divergence(fund, plotting=True)
    p.uptick()

    #print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[50, 25, 12]))
    #print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[200, 50, 25]))

    analysis['relative_strength'] = relative_strength(fund_name, fund_name, tickers=data, sector='', plot_output=True)
    analysis['features'] = {}

    p.uptick()

    hs, ma = feature_head_and_shoulders(fund)
    analysis['features']['head_shoulders'] = hs
    p.uptick()

    #print("")
    #print("")
    #print(f"{name} for {fund['Date'][len(fund['Date'])-1]}")
    #print("")
    #pprint.pprint(analysis['features'])
    #pprint.pprint(analysis['macd'])

slide_creator('2019')

print('Done.')
