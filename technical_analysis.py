import pandas as pd 
import numpy as np 

from libs import full_stochastic, ultimate_oscillator, cluster_oscs, name_parser, RSI

FILE = "securities/VHT.csv"

name = name_parser(FILE)
fund = pd.read_csv(FILE)

# std_sto = full_stochastic(fund, name=name)
# long_sto = full_stochastic(fund, config=[20,5,5], name=name)

# cluster_oscs(fund, name=name) 

ult = ultimate_oscillator(fund, name=name)
ult = ultimate_oscillator(fund, config=[5,10,20], name=name)

cluster_oscs(fund, function='ultimate', filter=3, name=name)

RSI(fund, name=name)