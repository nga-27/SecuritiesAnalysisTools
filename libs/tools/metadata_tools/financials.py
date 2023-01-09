import yfinance as yf


def get_financials(ticker: yf.Ticker) -> dict:
    """Get Financials

    Essentially JSON-serializes financial data from yfinance.

    Arguments:
        ticker {yf-object} -- yfinance data object

    Returns:
        dict -- finance data object
    """
    try:
        income = ticker.income_stmt
        financials = {index: list(row) for index, row in income.iterrows()}
        financials['dates'] = [col.strftime('%Y-%m-%d') for col in income.columns]

    except:
        financials = {}

    return financials