import yfinance as yf


def get_earnings(ticker: yf.Ticker) -> dict:
    """Get Earnings

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
        e_year['revenue'] = [rev for rev in year_earnings['Revenue']]
        e_year['earnings'] = [earn for earn in year_earnings['Earnings']]
        earnings['yearly'] = e_year

        quarter_earnings = ticker.quarterly_earnings
        e_quarter = {}
        e_quarter['period'] = list(quarter_earnings.index)
        e_quarter['revenue'] = [rev for rev in quarter_earnings['Revenue']]
        e_quarter['earnings'] = [earn for earn in quarter_earnings['Earnings']]
        earnings['quarterly'] = e_quarter

    except:
        earnings['yearly'] = {}
        earnings['quarterly'] = {}

    return earnings