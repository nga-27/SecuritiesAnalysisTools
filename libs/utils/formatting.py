import pandas as pd 
import numpy as np 
from datetime import datetime
import os 
import glob

def name_parser(name: str) -> str:
    """ parses file name to generate fund name """
    name = name.split('.')[0]
    name = name.split('/')
    name = name[len(name)-1]

    return name 


def dir_lister(sp_index: str='^GSPC.csv', directory: str='securities/'):
    file_ext = '*.csv'
    directory = directory + file_ext
    items = glob.glob(directory)
    index_file = None
    for item in items:
        if sp_index in item:
            index_file = item 
    return index_file, items
    