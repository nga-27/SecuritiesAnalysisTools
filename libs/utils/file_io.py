import os
import shutil
import glob
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta


def configure_temp_dir():
    """ for outputting, as well as temp files """
    if not os.path.exists('output/temp/'):
        if not os.path.exists('output/'):
            os.mkdir('output/')
        os.mkdir('output/temp/')


def remove_temp_dir():
    if os.path.exists('output/temp/'):
        shutil.rmtree('output/temp/')


def create_sub_temp_dir(name: str, sub_periods=[]):
    if not os.path.exists('output/temp/' + name + '/'):
        os.mkdir('output/temp/' + name + '/')
        if len(sub_periods) > 0:
            for period in sub_periods:
                if not os.path.exists('output/temp/' + name + '/' + period + '/'):
                    os.mkdir('output/temp/' + name + '/' + period + '/')


def windows_compatible_file_parse(extension: str, **kwargs) -> list:
    """File operations patch for Windows OS

    Arguments:
        extension {str} -- file extension

    Optional Args:
        parser {str} -- UNIX style directory (default: {'/'})
        desired_len {int} -- file extension length (default: {4})
        bad_parse {str} -- rendered extension to correct (default: {'\\'})

    Returns:
        list -- [description]
    """
    parser = kwargs.get('parser', '/')
    desired_len = kwargs.get('desired_len', 4)
    bad_parse = kwargs.get('bad_parse', '\\')

    globbed = extension.split(parser)
    if len(globbed) < desired_len:
        end = globbed[desired_len-2].split(bad_parse)
        globbed.pop(desired_len-2)
        globbed.append(end[0])
        globbed.append(end[1])
    return globbed
