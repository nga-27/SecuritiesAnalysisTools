import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os 
import shutil
import glob

def configure_temp_dir():
    """ for outputting, as well as temp files """
    if not os.path.exists('output/temp/'):
        if not os.path.exists('output/'):
            os.mkdir('output/')
        os.mkdir('output/temp/')


def remove_temp_dir():
    if os.path.exists('output/temp/'):
        shutil.rmtree('output/temp/')


def create_sub_temp_dir(name):
    if not os.path.exists('output/temp/' + name + '/'):
        os.mkdir('output/temp/' + name + '/')


def windows_compatible_file_parse(extension: str, parser: str='/', desired_len=4, bad_parse='\\') -> list:
    globbed = extension.split('/')
    if len(globbed) < desired_len:
        end = globbed[desired_len-2].split(bad_parse)
        globbed.pop(desired_len-2)
        globbed.append(end[0])
        globbed.append(end[1])
    return globbed