import pandas as pd 
import numpy as np 
import pprint 

from libs import full_stochastic, ultimate_oscillator, cluster_oscs, name_parser, RSI, get_trend_analysis
from libs import relative_strength
from libs import feature_head_and_shoulders

# https://stockcharts.com/school/doku.php?id=chart_school:overview:john_murphy_charting_made_easy

FILE = "securities/VNQ.csv"
fileB = "securities/VNQ.csv"

name = name_parser(FILE)
fund = pd.read_csv(FILE)
fundB = pd.read_csv(fileB)

# Start of automated process
analysis = {}

analysis['dates_covered'] = {'start': str(fund['Date'][0]), 'end': str(fund['Date'][len(fund['Date'])-1])}
analysis['name'] = name

chart, dat = cluster_oscs(fund, function='full_stochastic', filter_thresh=3, name=name) 
analysis['full_stochastic'] = dat
chart, dat = cluster_oscs(fund, function='ultimate', filter_thresh=3, name=name)
analysis['ultimate'] = dat  
chart, dat = cluster_oscs(fund, function='rsi', filter_thresh=3, name=name)
analysis['rsi'] = dat
chart, dat = cluster_oscs(fund, function='all', filter_thresh=3, name=name)
analysis['weighted'] = dat

#print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[50, 25, 12]))
#print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[200, 50, 25]))

analysis['relative_strength'] = relative_strength(fund, fundB, sector='')
analysis['features'] = {}

hs, ma = feature_head_and_shoulders(fundB)
analysis['features']['head_shoulders'] = hs

pprint.pprint(analysis)