import yfinance as yf


def get_cashflow(ticker: yf.Ticker) -> dict:
    """Get Cashflow

    Arguments:
        ticker {yf-object} -- yfinance data object

    Returns:
        dict -- Cashflow data object
    """
    try:
        cashflow = ticker.cashflow
        cash = {index: list(row) for index, row in cashflow.iterrows()}
        cash['dates'] = [col.strftime('%Y-%m-%d') for col in cashflow.columns]

    except:
        cash = {}

    return cash