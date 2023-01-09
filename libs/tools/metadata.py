import yfinance as yf

from libs.utils import STANDARD_COLORS, INDEXES, PRINT_CONSTANTS

from .metadata_tools import ( 
    dividends, fund_info, volatility, financials, balance_sheet, cashflow, earnings,
    recommendations, earnings_per_share, altman_z_score
)


WARNING = STANDARD_COLORS["warning"]
FUND = STANDARD_COLORS["ticker"]
NORMAL = STANDARD_COLORS["normal"]

REVERSE_LINE = PRINT_CONSTANTS["return_same_line"]


def get_api_metadata(fund_ticker: str, **kwargs) -> dict:
    """Get API Metadata

    Arguments:
        fund_ticker {str} -- fund name

    Optional Args:
        progress_bar {ProgressBar} -- (default: {None})
        plot_output {bool} -- 'Ratings by Firms' (default: {False})
        function {str} -- specific metadata functions (default: {'all'})

    Returns:
        dict -- contains all financial metadata available
    """
    pb = kwargs.get('progress_bar', None)
    plot_output = kwargs.get('plot_output', False)
    function = kwargs.get('function', 'all')

    fund_ticker_cleansed = INDEXES.get(fund_ticker, fund_ticker)
    api_print = f"\r\nFetching API metadata for {FUND}{fund_ticker_cleansed}{NORMAL}..."
    print(api_print)

    metadata = {}
    ticker = yf.Ticker(fund_ticker)
    if pb is not None:
        pb.uptick(increment=0.2)

    if function == 'all':
        metadata['dividends'] = dividends.get_dividends(ticker)

    if function == 'all' or function == 'info':
        metadata['info'] = fund_info.get_info(ticker)

    if function == 'all' or function == 'volatility':
        metadata['volatility'] = volatility.get_volatility(fund_ticker, plot_output=plot_output)
        if pb is not None:
            pb.uptick(increment=0.1)

    if ticker.info.get('holdings') or fund_ticker in INDEXES:
        # ETFs, Mutual Funds, and other indexes will have these but will output an ugly print
        # on financial data below, so let's just return what we have now.
        api_print += "  Canceled. (Fund is a mutual fund, ETF, or index.)"
        print(f"{REVERSE_LINE}{REVERSE_LINE}{REVERSE_LINE}{api_print}")
        return metadata

    if pb is not None:
        pb.uptick(increment=0.2)

    if function == 'all' or function == 'financials':
        metadata['financials'] = financials.get_financials(ticker)

    if function == 'all' or function == 'balance':
        metadata['balance_sheet'] = balance_sheet.get_balance_sheet(ticker)

    if pb is not None:
        pb.uptick(increment=0.1)

    if function == 'all':
        metadata['cashflow'] = cashflow.get_cashflow(ticker)
        metadata['earnings'] = earnings.get_earnings(ticker)

    if function == 'all' or function == 'recommendations':
        metadata['recommendations'] = recommendations.get_recommendations(ticker)
        metadata['recommendations']['tabular'] = recommendations.calculate_recommendation_curve(
            metadata['recommendations'], plot_output=plot_output, name=fund_ticker
        )

    if function == 'all':
        # EPS needs some other figures to make it correct, but ok for now.
        metadata['eps'] = earnings_per_share.calculate_eps(metadata)
        if pb is not None:
            pb.uptick(increment=0.1)

    if function == 'all':
        metadata['altman_z'] = altman_z_score.get_altman_z_score(metadata)

    api_print += "  Done."
    print(f"{REVERSE_LINE}{REVERSE_LINE}{REVERSE_LINE}{api_print}")

    return metadata
