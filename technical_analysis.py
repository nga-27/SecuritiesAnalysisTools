import pandas as pd 
import numpy as np 
import pprint 

from libs import full_stochastic, ultimate_oscillator, cluster_oscs, name_parser, RSI, get_trend_analysis
from libs import relative_strength
from libs import feature_head_and_shoulders

# https://stockcharts.com/school/doku.php?id=chart_school:overview:john_murphy_charting_made_easy

FILE = "securities/SLB.csv"
fileB = "securities/VDE.csv"

name = name_parser(FILE)
fund = pd.read_csv(FILE)
fundB = pd.read_csv(fileB)

#std_sto = full_stochastic(fund, name=name)
#long_sto = full_stochastic(fund, config=[20,5,5], name=name)

#cluster_oscs(fund, name=name) 

#ult = ultimate_oscillator(fund, name=name)
#ult = ultimate_oscillator(fund, config=[5,10,20], name=name)

#cluster_oscs(fund, function='ultimate', filter_thresh=3, name=name) 

#RSI(fund, name=name)

#cluster_oscs(fund, function='rsi', filter_thresh=3, name=name)
#cluster_oscs(fund, function='all', filter_thresh=3, name=name)

#print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[50, 25, 12]))
#print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[200, 50, 25]))

pprint.pprint(relative_strength(fund, fundB, sector='VDE'))

hs, ma = feature_head_and_shoulders(fundB)
#pprint.pprint(hs['features'])