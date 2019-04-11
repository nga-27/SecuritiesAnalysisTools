import pandas as pd 
import numpy as np 

from libs import full_stochastic, ultimate_oscillator, cluster_oscs

fund = pd.read_csv("securities/AMD.csv")

std_sto = full_stochastic(fund)
long_sto = full_stochastic(fund, config=[20,5,5])

cluster_oscs(fund) 

ult = ultimate_oscillator(fund)
ult = ultimate_oscillator(fund, config=[5,10,20])
