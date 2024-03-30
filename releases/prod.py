"""
#   Technical Analysis Tools
#
#   by: nga-27
#
#   A program that outputs a graphical and a numerical analysis of
#   securities (stocks, bonds, equities, and the like). Analysis
#   includes use of oscillators (Stochastic, relative_strength_indicator_rsi, and Ultimate),
#   momentum charting (Moving Average Convergence Divergence,
#   Simple and Exponential Moving Averages), trend analysis (Bands,
#   Support and Resistance, Channels), and some basic feature
#   detection (Head and Shoulders, Pennants).
#
"""
from typing import Tuple

# Imports that are custom tools that are the crux of this program
from libs.tools import (
    ultimate_oscillator, cluster_oscillators, relative_strength_indicator_rsi,
    relative_strength, moving_average_swing_trade, triple_moving_average, triple_exp_mov_average,
    mov_avg_convergence_divergence, on_balance_volume, find_resistance_support_lines,
    get_trend_lines, get_high_level_stats, bollinger_bands, candlesticks, risk_comparison,
    average_true_range, average_directional_index, get_api_metadata
)

# Imports that are generic file/string/object/date utility functions
from libs.utils import (
    date_extractor, create_sub_temp_dir, INDEXES, SKIP_INDEXES, ProgressBar, start_clock
)

# Imports that drive custom metrics for market analysis
from libs.metrics.content_list import assemble_last_signals
from libs.metrics.metrics_utils import future_returns
from libs.metrics.synopsis import generate_synopsis

####################################################################
####################################################################


def run_prod(script: list) -> Tuple[dict, float]:
    """Run Production Script

    Script that has stabilized functions

    Arguments:
        script {list} -- dataset, funds, periods, config

    Returns:
        Tuple[dict, float] -- analysis object of fund data, clock time
    """
    # pylint: disable=too-many-locals,too-many-statements
    dataset = script[0]
    funds = script[1]
    periods = script[2]
    config = script[3]

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
            fund_data['dates_covered'] = {'start': str(start), 'end': str(end)}
            fund_data['name'] = fund_name

            fund_print2 = fund_print + f" ({period}) "
            prog_bar = ProgressBar(config['process_steps'], name=fund_print2, offset=clock)
            prog_bar.start()

            fund_data['statistics'] = get_high_level_stats(fund)
            fund_data['clustered_osc'] = cluster_oscillators(
                fund,
                function='all',
                filter_thresh=3,
                name=fund_name,
                plot_output=False,
                progress_bar=prog_bar,
                view=period)

            fund_data['rsi'] = relative_strength_indicator_rsi(
                fund, name=fund_name, plot_output=False,
                out_suppress=False, progress_bar=prog_bar, view=period)

            fund_data['ultimate'] = ultimate_oscillator(
                fund, name=fund_name, plot_output=False,
                out_suppress=False, progress_bar=prog_bar, view=period)

            fund_data['on_balance_volume'] = on_balance_volume(
                fund, plot_output=False, name=fund_name, progress_bar=prog_bar, view=period)

            fund_data['simple_moving_average'] = triple_moving_average(
                fund, plot_output=False, name=fund_name, progress_bar=prog_bar, view=period)

            fund_data['exp_moving_average'] = triple_exp_mov_average(
                fund, plot_output=False, name=fund_name, progress_bar=prog_bar, view=period)

            fund_data['sma_swing_trade'] = moving_average_swing_trade(
                fund, plot_output=False, name=fund_name, progress_bar=prog_bar, view=period)

            fund_data['ema_swing_trade'] = moving_average_swing_trade(
                fund, function='ema', plot_output=False,
                name=fund_name, progress_bar=prog_bar, view=period)

            fund_data['macd'] = mov_avg_convergence_divergence(
                fund, plot_output=False, name=fund_name, progress_bar=prog_bar, view=period)

            fund_data['bollinger_bands'] = bollinger_bands(
                fund, plot_output=False, name=fund_name, progress_bar=prog_bar, view=period)

            fund_data['average_true_range'] = average_true_range(
                fund, plot_output=False, name=fund_name, progress_bar=prog_bar, view=period)

            fund_data['adx'] = average_directional_index(
                fund, atr=fund_data['average_true_range']['tabular'], plot_output=False,
                name=fund_name, progress_bar=prog_bar, view=period)

            if 'no_index' not in config['state']:
                strength, match_data = relative_strength(
                    fund_name,
                    full_data_dict=dataset[period],
                    config=config,
                    plot_output=False,
                    meta=analysis[fund_name]['metadata'],
                    progress_bar=prog_bar,
                    period=period,
                    interval=config['interval'][i],
                    view=period
                )
                fund_data['relative_strength'] = strength

                fund_data['statistics']['risk_ratios'] = risk_comparison(
                    fund, dataset[period]['^GSPC'], dataset[period]['^IRX'],
                    sector_data=match_data)
                prog_bar.uptick()

            # Support and Resistance Analysis
            fund_data['support_resistance'] = find_resistance_support_lines(
                fund, name=fund_name, plot_output=False, progress_bar=prog_bar, view=period)

            # Feature Detection Block
            # fund_data['features'] = {}
            # fund_data['features']['head_shoulders'] = feature_detection_head_and_shoulders(
            #     fund, name=fund_name, plot_output=False, progress_bar=prog_bar, view=period)

            fund_data['candlesticks'] = candlesticks(
                fund, name=fund_name, plot_output=False, view=period, progress_bar=prog_bar)

            # fund_data['price_gaps'] = analyze_price_gaps(
            #     fund, name=fund_name, plot_output=False, progress_bar=prog_bar, view=period)

            # Get Trendlines
            fund_data['trendlines'] = get_trend_lines(
                fund,
                name=fund_name,
                plot_output=False,
                progress_bar=prog_bar,
                view=period,
                meta=analysis[fund_name]['metadata'])

            # Various Fund-specific Metrics
            fund_data['futures'] = future_returns(fund, progress_bar=prog_bar)

            # Parse through indicators and pull out latest signals (must be last)
            fund_data['last_signals'] = assemble_last_signals(
                fund_data, fund=fund, name=fund_name, view=period,
                progress_bar=prog_bar, plot_output=False)

            prog_bar.end()
            analysis[fund_name][period] = fund_data

        analysis[fund_name]['synopsis'] = generate_synopsis(
            analysis, name=fund_name)

    return analysis, clock
