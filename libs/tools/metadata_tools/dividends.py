import yfinance as yf


def get_dividends(ticker: yf.Ticker, symbol=None):
    """Get Dividends

    Will run yfinance API if ticker is None and symbol is not None. Essentially JSON-serializes
    dividends data from yfinance. 

    Arguments:
        ticker {yf-object} -- ticker object from yfinance

    Keyword Arguments:
        symbol {str} -- ticker symbol (default: {None})

    Returns:
        dict -- dividend data object
    """
    divs = {}
    if ticker is None and symbol is not None:
        ticker = yf.Ticker(symbol)

    try:
        tick_divs = ticker.dividends
        divs['dates'] = [date.strftime("%Y-%m-%d") for date in tick_divs.keys()]
        divs['dividends'] = [tick_divs[date] for date in tick_divs.keys()]
    except:
        divs['dividends'] = []
        divs['dates'] = []
    return divs
