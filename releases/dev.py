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
from libs.tools import relative_strength, moving_average_swing_trade
from libs.tools import triple_moving_average, triple_exp_mov_average
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
from libs.tools import commodity_channel_index
from libs.tools import candlesticks
from libs.tools import risk_comparison
from libs.tools import rate_of_change_oscillator
from libs.tools import know_sure_thing
from libs.tools import average_true_range

# Imports that support functions doing feature detection
from libs.features import feature_detection_head_and_shoulders
from libs.features import analyze_price_gaps

# Imports that are generic file/string/object/date utility functions
from libs.utils import date_extractor
from libs.utils import create_sub_temp_dir
from libs.utils import get_api_metadata
from libs.utils import INDEXES, SKIP_INDEXES

# Imports that drive custom metrics for market analysis
from libs.metrics import future_returns
from libs.metrics import generate_synopsis
from libs.metrics import assemble_last_signals

# Imports that start process and show progress doing so
from libs.utils import ProgressBar, start_clock

# Imports in development / non-final "public" calls
from test import test_competitive

####################################################################
####################################################################


def run_dev(script: list):
    """Run Development Script

    Script that is for implementing new content

    Arguments:
        script {list} -- dataset, funds, periods, config

    Returns:
        dict -- analysis object of fund data
    """
    dataset = script[0]
    funds = script[1]
    periods = script[2]
    config = script[3]

    # Start of automated process
    analysis = {}
    clock = start_clock()

    for fund_name in funds:

        if fund_name in SKIP_INDEXES:
            continue

        fund_print = INDEXES.get(fund_name, fund_name)
        print("")
        print(f"~~{fund_print}~~")
        create_sub_temp_dir(fund_name, sub_periods=config['period'])

        analysis[fund_name] = {}

        analysis[fund_name]['metadata'] = get_api_metadata(
            fund_name,
            max_close=max(dataset[periods[0]][fund_name]['Close']),
            data=dataset[periods[0]][fund_name])

        ###################### START OF PERIOD LOOPING #############################
        for i, period in enumerate(periods):
            fund_data = {}

            fund = dataset[period][fund_name]

            start = date_extractor(fund.index[0], _format='str')
            end = date_extractor(fund.index[-1], _format='str')
            fund_data['dates_covered'] = {
                'start': str(start), 'end': str(end)}
            fund_data['name'] = fund_name

            fund_print2 = fund_print + f" ({period}) "
            p = ProgressBar(config['process_steps'],
                            name=fund_print2, offset=clock)
            p.start()

            fund_data['statistics'] = get_high_level_stats(fund)

            fund_data['clustered_osc'] = cluster_oscs(
                fund,
                function='all',
                filter_thresh=3,
                name=fund_name,
                plot_output=False,
                progress_bar=p,
                view=period)

            fund_data['full_stochastic'] = full_stochastic(
                fund, name=fund_name, plot_output=False, out_suppress=False, progress_bar=p, view=period)

            fund_data['rsi'] = RSI(
                fund, name=fund_name, plot_output=False, out_suppress=False, progress_bar=p, view=period)

            fund_data['ultimate'] = ultimate_oscillator(
                fund, name=fund_name, plot_output=False, out_suppress=False, progress_bar=p, view=period)

            fund_data['awesome'] = awesome_oscillator(
                fund, name=fund_name, plot_output=False, progress_bar=p, view=period)

            fund_data['momentum_oscillator'] = momentum_oscillator(
                fund, name=fund_name, plot_output=False, progress_bar=p, view=period)

            fund_data['on_balance_volume'] = on_balance_volume(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['simple_moving_average'] = triple_moving_average(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['exp_moving_average'] = triple_exp_mov_average(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['sma_swing_trade'] = moving_average_swing_trade(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['ema_swing_trade'] = moving_average_swing_trade(
                fund, function='ema', plot_output=False,
                name=fund_name, progress_bar=p, view=period)

            fund_data['hull_moving_average'] = hull_moving_average(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['macd'] = mov_avg_convergence_divergence(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['bear_bull_power'] = bear_bull_power(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['total_power'] = total_power(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['bollinger_bands'] = bollinger_bands(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['commodity_channels'] = commodity_channel_index(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['rate_of_change'] = rate_of_change_oscillator(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['know_sure_thing'] = know_sure_thing(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            fund_data['average_true_range'] = average_true_range(
                fund, plot_output=False, name=fund_name, progress_bar=p, view=period)

            if 'no_index' not in config['state']:
                strength, match_data = relative_strength(
                    fund_name,
                    full_data_dict=dataset[period],
                    config=config,
                    plot_output=False,
                    meta=analysis[fund_name]['metadata'],
                    progress_bar=p,
                    period=period,
                    interval=config['interval'][i],
                    view=period
                )
                fund_data['relative_strength'] = strength

                fund_data['statistics']['risk_ratios'] = risk_comparison(
                    fund, dataset[period]['^GSPC'], dataset[period]['^IRX'],
                    sector_data=match_data)
                p.uptick()

            # Support and Resistance Analysis
            fund_data['support_resistance'] = find_resistance_support_lines(
                fund, name=fund_name, plot_output=False, progress_bar=p, view=period)

            # Feature Detection Block
            fund_data['features'] = {}
            fund_data['features']['head_shoulders'] = feature_detection_head_and_shoulders(
                fund, name=fund_name, plot_output=False, progress_bar=p, view=period)

            fund_data['candlesticks'] = candlesticks(
                fund, name=fund_name, plot_output=False, view=period, progress_bar=p)

            fund_data['price_gaps'] = analyze_price_gaps(
                fund, name=fund_name, plot_output=False, progress_bar=p, view=period)

            # Get Trendlines
            fund_data['trendlines'] = get_trendlines(
                fund,
                name=fund_name,
                plot_output=False,
                progress_bar=p,
                view=period,
                meta=analysis[fund_name]['metadata'])

            # Various Fund-specific Metrics
            fund_data['futures'] = future_returns(fund, progress_bar=p)

            # Parse through indicators and pull out latest signals (must be last)
            fund_data['last_signals'] = assemble_last_signals(
                fund_data, fund=fund, name=fund_name, view=period,
                progress_bar=p, plot_output=False)

            p.end()

            analysis[fund_name][period] = fund_data

        analysis[fund_name]['synopsis'] = generate_synopsis(
            analysis, name=fund_name)

    return analysis, clock
