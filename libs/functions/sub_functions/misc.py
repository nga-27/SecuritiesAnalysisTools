from libs.tools import (
    relative_strength, get_api_metadata, risk_comparison
)

from .utils import (
    TICKER, NORMAL, function_data_download, function_sector_match
)


def relative_strength_function(config: dict):
    config['tickers'] += ' ^GSPC'
    data, fund_list = function_data_download(config)
    for fund in fund_list:
        if fund != '^GSPC':
            print(
                f"Relative Strength of {TICKER}{fund}{NORMAL} compared to S&P500...")
            relative_strength(fund, full_data_dict=data,
                              config=config, plot_output=True)


def risk_function(config: dict):
    print(f"Risk Factors for funds...\r\n")
    config['tickers'] += ' ^GSPC ^IRX'
    data, fund_list = function_data_download(config)

    for fund in fund_list:
        if fund != '^GSPC' and fund != '^IRX':
            print(
                f"\r\nRisk Factors of {TICKER}{fund}{NORMAL}...")

            meta_fund = get_api_metadata(fund, function='info')
            match_fund, match_data = function_sector_match(
                meta_fund, data[fund], config)

            if match_fund is not None:
                match_data = match_data.get(match_fund, data.get(match_fund))

            risk_comparison(data[fund], data['^GSPC'],
                            data['^IRX'], print_out=True, sector_data=match_data)
            print("------")