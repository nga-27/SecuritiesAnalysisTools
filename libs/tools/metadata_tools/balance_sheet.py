import yfinance as yf


def get_balance_sheet(ticker: yf.Ticker) -> dict:
    """Get Balance Sheet

    Arguments:
        ticker {yf-object} -- yfinance data object

    Returns:
        dict -- Balance Sheet data object
    """
    try:
        balance_sheet = ticker.balance_sheet
        bal = {index: list(row) for index, row in balance_sheet.iterrows()}
        bal['dates'] = [col.strftime('%Y-%m-%d') for col in balance_sheet.columns]

    except:
        balance_sheet = {}

    return balance_sheet