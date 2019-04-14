import pandas as pd 
import numpy as np 

from libs import full_stochastic, ultimate_oscillator, cluster_oscs, name_parser, RSI, get_trend_analysis

FILE = "securities/AMD.csv"

name = name_parser(FILE)
fund = pd.read_csv(FILE)

#std_sto = full_stochastic(fund, name=name)
#long_sto = full_stochastic(fund, config=[20,5,5], name=name)

#cluster_oscs(fund, name=name) 

#ult = ultimate_oscillator(fund, name=name)
#ult = ultimate_oscillator(fund, config=[5,10,20], name=name)

cluster_oscs(fund, function='ultimate', filter_thresh=3, name=name) 

#RSI(fund, name=name)

cluster_oscs(fund, function='rsi', filter_thresh=3, name=name)
cluster_oscs(fund, function='all', filter_thresh=3, name=name)

print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[50, 25, 12]))
print(get_trend_analysis(fund, date_range=['2019-02-01', '2019-04-14'], config=[200, 50, 25]))