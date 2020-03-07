"""
#   Technical Analysis Tools
#
#   by: nga-27
#
#   A program that outputs a graphical and a numerical analysis of
#   securities (stocks, bonds, equities, and the like). Analysis 
#   includes use of oscillators (Stochastic, RSI, and Ultimate), 
#   momentum charting (Moving Average Convergence Divergence, 
#   Simple and Exponential Moving Averages), trend analysis (Bands, 
#   Support and Resistance, Channels), and some basic feature 
#   detection (Head and Shoulders, Pennants).
#   
"""

# Imports that are custom tools that are the crux of this program
from libs.tools import full_stochastic, ultimate_oscillator, cluster_oscs, RSI
from libs.tools import awesome_oscillator, momentum_oscillator
from libs.tools import relative_strength, triple_moving_average, moving_average_swing_trade
from libs.tools import hull_moving_average
from libs.tools import mov_avg_convergence_divergence
from libs.tools import on_balance_volume
from libs.tools import beta_comparison
from libs.tools import find_resistance_support_lines
from libs.tools import get_trendlines, get_trend_analysis
from libs.tools import get_high_level_stats
from libs.tools import bear_bull_power
from libs.tools import total_power
from libs.tools import bollinger_bands

# Imports that support functions doing feature detection
from libs.features import feature_detection_head_and_shoulders, feature_plotter, analyze_price_gaps

# Imports that are generic file/string/object/date utility functions
from libs.utils import name_parser, fund_list_extractor, index_extractor, index_appender, date_extractor
from libs.utils import configure_temp_dir, remove_temp_dir, create_sub_temp_dir
from libs.utils import download_data_all, has_critical_error, get_api_metadata
from libs.utils import TEXT_COLOR_MAP, SP500

# Imports that control function-only inputs
from libs.functions import only_functions_handler

# Imports that plot (many are imported in functions)
from libs.utils import candlestick

# Imports that drive custom metrics for market analysis
from libs.metrics import market_composite_index, bond_composite_index
from libs.metrics import correlation_composite_index, type_composite_index
from libs.metrics import future_returns, metadata_to_dataset

# Imports that create final products and show progress doing so
from libs.utils import ProgressBar, start_header
from libs.outputs import slide_creator, output_to_json

# Imports in development / non-final "public" calls
from test import test_competitive

####################################################################
####################################################################

################################
_VERSION_ = '0.1.27'
_DATE_REVISION_ = '2020-03-07'
################################
PROCESS_STEPS_DEV = 21

HEADER_COLOR = TEXT_COLOR_MAP["blue"]
NORMAL_COLOR = TEXT_COLOR_MAP["white"]


def technical_analysis(config: dict):

    config['process_steps'] = PROCESS_STEPS_DEV
    if config['release'] == True:
        # Use only after release!
        print(" ")
        print(
            f"{HEADER_COLOR}~~~~ DEVELOPMENT VERSION ~~~~ [latest functionality, 'unclean' version]{NORMAL_COLOR}")
        config = start_header(update_release=_DATE_REVISION_,
                              version=_VERSION_, options=True)
        config['process_steps'] = PROCESS_STEPS_DEV

    if config['state'] == 'halt':
        return

    if 'function' in config['state']:
        # If only simple functions are desired, they go into this handler
        only_functions_handler(config)
        return

    if 'no_index' not in config['state']:
        config['tickers'] = index_appender(config['tickers'])
        config['process_steps'] = config['process_steps'] + 2

    # Temporary directories to save graphs as images, etc.
    remove_temp_dir()
    configure_temp_dir()

    dataset, funds, periods, config = download_data_all(config=config)

    for period in dataset:
        e_check = {'tickers': config['tickers']}
        if has_critical_error(dataset[period], 'download_data', misc=e_check):
            return None

    # Start of automated process
    analysis = {}

    for fund_name in funds:

        fund_print = SP500.get(fund_name, fund_name)
        print("")
        print(f"~~{fund_print}~~")
        create_sub_temp_dir(fund_name, sub_periods=config['period'])

        analysis[fund_name] = {}

        analysis[fund_name]['metadata'] = get_api_metadata(
            fund_name,
            max_close=max(dataset[periods[0]][fund_name]['Close']),
            data=dataset[periods[0]][fund_name])

        for i, period in enumerate(periods):

            fund_data = {}

            fund = dataset[period][fund_name]

            start = date_extractor(fund.index[0], _format='str')
            end = date_extractor(
                fund.index[len(fund['Close'])-1], _format='str')
            fund_data['dates_covered'] = {
                'start': str(start), 'end': str(end)}
            fund_data['name'] = fund_name

            fund_print2 = fund_print + f" ({period}) "
            p = ProgressBar(config['process_steps'], name=fund_print2)
            p.start()

            fund_data['statistics'] = get_high_level_stats(fund)

            fund_data['clustered_osc'] = cluster_oscs(fund, function='all', filter_thresh=3,
                                                      name=fund_name, plot_output=False, progress_bar=p)

            fund_data['full_stochastic'] = full_stochastic(
                fund, name=fund_name, plot_output=False, out_suppress=False, progress_bar=p)

            fund_data['rsi'] = RSI(
                fund, name=fund_name, plot_output=False, out_suppress=False, progress_bar=p)

            fund_data['ultimate'] = ultimate_oscillator(
                fund, name=fund_name, plot_output=False, out_suppress=False, progress_bar=p)

            fund_data['awesome'] = awesome_oscillator(
                fund, name=fund_name, plot_output=False, progress_bar=p)

            fund_data['momentum_oscillator'] = momentum_oscillator(
                fund, name=fund_name, plot_output=False, progress_bar=p)

            fund_data['obv'] = on_balance_volume(
                fund, plot_output=False, name=fund_name, progress_bar=p)

            fund_data['moving_average'] = triple_moving_average(
                fund, plot_output=False, name=fund_name, progress_bar=p)

            fund_data['swing_trade'] = moving_average_swing_trade(
                fund, plot_output=False, name=fund_name, progress_bar=p)

            fund_data['hull_moving_average'] = hull_moving_average(
                fund, plot_output=False, name=fund_name, progress_bar=p)

            fund_data['macd'] = mov_avg_convergence_divergence(
                fund, plot_output=False, name=fund_name, progress_bar=p)

            fund_data['bear_bull_power'] = bear_bull_power(
                fund, plot_output=False, name=fund_name, progress_bar=p)

            fund_data['total_power'] = total_power(
                fund, plot_output=False, name=fund_name, progress_bar=p)

            fund_data['bollinger_bands'] = bollinger_bands(
                fund, plot_output=False, name=fund_name, progress_bar=p)

            if 'no_index' not in config['state']:
                fund_data['relative_strength'] = relative_strength(
                    fund_name,
                    full_data_dict=dataset[period],
                    config=config,
                    plot_output=False,
                    meta=analysis[fund_name]['metadata'],
                    progress_bar=p,
                    period=period,
                    interval=config['interval'][i]
                )

                beta, rsqd = beta_comparison(fund, dataset[period]['^GSPC'])
                fund_data['beta'] = beta
                fund_data['r_squared'] = rsqd
                p.uptick()

            # Support and Resistance Analysis
            fund_data['support_resistance'] = find_resistance_support_lines(
                fund, name=fund_name, plot_output=False, progress_bar=p)

            # Feature Detection Block
            fund_data['features'] = {}
            fund_data['features']['head_shoulders'] = feature_detection_head_and_shoulders(
                fund, name=fund_name, plot_output=False, progress_bar=p)

            filename = f"{fund_name}/candlestick_{fund_name}"
            candlestick(fund, title=fund_print, filename=filename,
                        saveFig=True, progress_bar=p)

            fund_data['price_gaps'] = analyze_price_gaps(
                fund, name=fund_name, plot_output=False, progress_bar=p)

            # Get Trendlines
            fund_data['trendlines'] = get_trendlines(
                fund, name=fund_name, plot_output=False, progress_bar=p)

            # Various Fund-specific Metrics
            fund_data['futures'] = future_returns(
                fund, to_json=True, progress_bar=p)

            p.end()

            analysis[fund_name][period] = fund_data

    analysis['_METRICS_'] = {}
    analysis['_METRICS_']['mci'] = market_composite_index(
        config=config, plot_output=False)

    bond_composite_index(config=config, plot_output=False)

    analysis['_METRICS_']['correlation'] = correlation_composite_index(
        config=config, plot_output=False)

    analysis['_METRICS_']['tci'] = type_composite_index(
        config=config, plot_output=False)

    # slide_creator(analysis, config=config)
    output_to_json(analysis)

    metadata_to_dataset(config=config)

    remove_temp_dir()
