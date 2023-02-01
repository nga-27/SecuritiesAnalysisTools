""" Formatting Utility """
from datetime import datetime
import pandas as pd


def index_extractor(tickers) -> str:
    """ tickers is a str of tickers, separated by a space """
    potential_indexes = ['^GSPC']
    ind = None

    for key in potential_indexes:
        if key in tickers:
            ind = key

    return ind


def index_appender(tickers: str) -> str:
    """ appends ^GSPC to ticker string """
    tickers = tickers + ' ' + '^GSPC' + ' ' + '^IRX'
    return tickers


def fund_list_extractor(ticker_df: dict, config: dict = None) -> list:
    """Fund List Extractor

    Extracts fund names from ticker_df for accessing later

    Arguments:
        ticker_df {dict} -- fund dataset

    Keyword Arguments:
        config {dict} -- controlling dict (default: {None})

    Returns:
        list -- ticker funds
    """
    funds = []
    if config is not None:
        # First check if a single fund (single dimension), only on 0.1.13+
        if 'Open' in ticker_df:
            funds = [config['tickers']]
            return funds

    for key in ticker_df:
        # Multi-level df, so we need to extract only name key (remove duplicates)
        if (len(key) > 1) and (key[0] not in funds):
            funds.append(key[0])

    return funds


def dates_extractor_list(data_frame: pd.DataFrame) -> list:
    """Dates Extractor to List

    Arguments:
        df {pd.DataFrame, list} -- dataframe with dates as the 'index'

    Returns:
        list -- list of dates separated '%Y-%m-%d' or indexes (for a list)
    """
    dates = []
    if isinstance(data_frame, list):
        for i in range(len(data_frame)):
            dates.append(i)

    else:
        for date_item in data_frame.index:
            date = str(date_item)
            date = date.split(' ', maxsplit=1)[0]
            date = datetime.strptime(date, '%Y-%m-%d')
            dates.append(date)

    return dates


def date_extractor(date, _format=None):
    """Date Extractor

    Converts a date object into either a string date ('%Y-%m-%d'), an iso-format datetime object,
    or a normal datetime object.

    Arguments:
        date {datetime} -- datetime object, typically

    Keyword Arguments:
        _format {str} -- either 'str' or 'iso' to control output format (default: {None})

    Returns:
        str, datetime -- either a string or datetime object
    """
    date = str(date)
    date1 = date.split(' ', maxsplit=1)[0]
    date2 = datetime.strptime(date1, '%Y-%m-%d')
    if _format == 'str':
        date_val = date1
    elif _format == 'iso':
        date_val = date2.isoformat()
    else:
        date_val = date2
    return date_val


def dates_convert_from_index(data_frame: pd.DataFrame, list_of_xlists: list, to_str=False) -> list:
    """Dates Convert from Index

    Used primarily with various plots and complex plotting (e.g. "shapes")

    Arguments:
        df {pd.DataFrame} -- fund dataset
        list_of_xlists {list} -- lists of standard x ranges of indexes needed for conversion to
                                 lists of dates

    Keyword Arguments:
        to_str {bool} -- if True, convert to ('%Y-%m-%d') (default: {False})

    Returns:
        list -- list of new dates or list of list of new dates
    """
    new_l_of_xls = []
    if len(list_of_xlists) > 0:
        for xlist in list_of_xlists:
            new_xlist = []
            for x_val in xlist:
                if to_str:
                    date = data_frame.index[x_val].strftime("%Y-%m-%d")
                else:
                    date = data_frame.index[x_val]
                new_xlist.append(date)
            new_l_of_xls.append(new_xlist)
    return new_l_of_xls
