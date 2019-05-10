import pandas as pd 
import numpy as np 
import pprint 

from libs.tools import full_stochastic, ultimate_oscillator, cluster_oscs, RSI
from libs.tools import relative_strength, triple_moving_average
from libs.features import feature_head_and_shoulders

from libs.tools import get_trend_analysis, mov_avg_convergence_divergence, on_balance_volume
from libs.utils import name_parser, dir_lister
from libs.metrics import nasit_composite_index

# https://stockcharts.com/school/doku.php?id=chart_school:overview:john_murphy_charting_made_easy

FILE = "securities/VGT.csv"
#fileB = "securities/VNQ.csv"
fileB = FILE

sp500_index, files_to_parse = dir_lister()

files_to_parse = [FILE]

for FILE in files_to_parse:

    name = name_parser(FILE)
    fund = pd.read_csv(FILE)
    fundB = pd.read_csv(fileB)

    # Start of automated process
    analysis = {}

    analysis['dates_covered'] = {'start': str(fund['Date'][0]), 'end': str(fund['Date'][len(fund['Date'])-1])}
    analysis['name'] = name

    #full_stochastic(fund, name=name)

    #chart, dat = cluster_oscs(fund, function='full_stochastic', filter_thresh=3, name=name) 
    #analysis['full_stochastic'] = dat
    #chart, dat = cluster_oscs(fund, function='ultimate', filter_thresh=3, name=name)
    #analysis['ultimate'] = dat  
    #chart, dat = cluster_oscs(fund, function='rsi', filter_thresh=3, name=name)
    #analysis['rsi'] = dat
    chart, dat = cluster_oscs(fund, function='all', filter_thresh=3, name=name)
    analysis['weighted'] = dat

    on_balance_volume(fund)

    triple_moving_average(fund)

    #analysis['rsi'] = RSI(fund, name=name)
    #analysis['ultimate'] = ultimate_oscillator(fund, name=name)

    analysis['macd'] = mov_avg_convergence_divergence(fund)

    #print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[50, 25, 12]))
    #print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[200, 50, 25]))

    analysis['relative_strength'] = relative_strength(fund, fundB, sector='')
    analysis['features'] = {}

    hs, ma = feature_head_and_shoulders(fund)
    analysis['features']['head_shoulders'] = hs

    print("")
    print("")
    print(f"{name} for {fund['Date'][len(fund['Date'])-1]}")
    print("")
    pprint.pprint(analysis['features'])
    pprint.pprint(analysis['macd'])
    print(analysis['weighted']['nasit'])
    print(analysis['macd']['nasit'])
    #print(nasit_composite_index(fund))
    #nasit_composite_index(fund)

print('Done.')
