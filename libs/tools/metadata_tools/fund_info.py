""" Fund Information """
import yfinance as yf


def get_info(ticker: yf.Ticker) -> dict:
    """Get Info

    Arguments:
        ticker {yf-object} -- ticker object from yfinance

    Returns:
        dict -- fund info data object
    """
    try:
        info = dict(ticker.info)
        info['marketCap'] = ticker.fast_info.get('market_cap')
    except: # pylint: disable=bare-except
        info = {}
    return info
