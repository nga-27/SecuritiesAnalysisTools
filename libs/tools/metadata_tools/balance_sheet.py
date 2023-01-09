import yfinance as yf


def get_balance_sheet(ticker: yf.Ticker) -> dict:
    """Get Balance Sheet

    Essentially JSON-serializes balance sheet data from yfinance.

    Arguments:
        ticker {yf-object} -- yfinance data object

    Returns:
        dict -- Balance Sheet data object
    """
    try:
        balance = ticker.balance_sheet
        balance_sheet = {index: list(row) for index, row in balance.iterrows()}
        balance_sheet['dates'] = [col.strftime('%Y-%m-%d') for col in balance.columns]

    except:
        balance_sheet = {}

    return balance_sheet