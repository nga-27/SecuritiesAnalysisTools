import yfinance as yf


def get_info(ticker: yf.Ticker) -> dict:
    """Get Info

    Arguments:
        ticker {yf-object} -- ticker object from yfinance

    Returns:
        dict -- fund info data object
    """
    try:
        info = ticker.info
    except:
        info = {}
    return info
