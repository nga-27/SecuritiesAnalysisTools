import pandas as pd 
import numpy as np 
from datetime import datetime

def name_parser(name: str) -> str:
    """ parses file name to generate fund name """
    name = name.split('.')[0]
    name = name.split('/')
    name = name[len(name)-1]

    return name 

