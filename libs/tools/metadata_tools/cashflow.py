""" Cashflow """
import yfinance as yf


def get_cashflow(ticker: yf.Ticker) -> dict:
    """Get Cashflow

    Essentially JSON-serializes cash flow data from yfinance.

    Arguments:
        ticker {yf-object} -- yfinance data object

    Returns:
        dict -- Cashflow data object
    """
    try:
        cashflow = ticker.cashflow
        cash = {index: list(row) for index, row in cashflow.iterrows()}
        cash['dates'] = [col.strftime('%Y-%m-%d') for col in cashflow.columns]

    except: # pylint: disable=bare-except
        cash = {}

    return cash
