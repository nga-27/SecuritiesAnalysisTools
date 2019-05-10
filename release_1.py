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
from time import sleep 

from libs.utils import ProgressBar


# A List of Items
items = list(range(0, 57))
l = len(items)

p = ProgressBar(l, name='VGT')
q = ProgressBar(l, name='VNQ')

p.start()
q.start()
for i, item in enumerate(items):
    sleep(0.1)
    p.uptick()
for i, item in enumerate(items):
    sleep(0.15)
    q.uptick()


print('done')
