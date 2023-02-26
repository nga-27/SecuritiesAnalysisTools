""" Earnings """
import yfinance as yf


def get_earnings(ticker: yf.Ticker) -> dict:
    """Get Earnings

    Essentially JSON-serializes earnings data from yfinance.

    Arguments:
        ticker {yf-object} -- yfinance data object

    Returns:
        dict -- Earnings data object
    """
    earnings = {}

    try:
        year_earnings = ticker.earnings
        e_year = {}
        e_year['period'] = list(year_earnings.index)
        e_year['revenue'] = list(year_earnings['Revenue'])
        e_year['earnings'] = list(year_earnings['Earnings'])
        earnings['yearly'] = e_year

        quarter_earnings = ticker.quarterly_earnings
        e_quarter = {}
        e_quarter['period'] = list(quarter_earnings.index)
        e_quarter['revenue'] = list(quarter_earnings['Revenue'])
        e_quarter['earnings'] = list(quarter_earnings['Earnings'])
        earnings['quarterly'] = e_quarter

    except: # pylint: disable=bare-except
        earnings['yearly'] = {}
        earnings['quarterly'] = {}

    return earnings
