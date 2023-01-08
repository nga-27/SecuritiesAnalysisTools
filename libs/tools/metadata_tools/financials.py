import yfinance as yf


def get_financials(ticker: yf.Ticker) -> dict:
    """Get Financials

    Arguments:
        ticker {yf-object} -- yfinance data object
        st {yf-object} -- ticker object from yfinance (0.1.50)

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