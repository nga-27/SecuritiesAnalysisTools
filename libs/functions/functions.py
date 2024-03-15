""" functions to be used a single operations (or eventual API functions) """
from types import FunctionType

from libs.tools import (
    get_trend_lines, find_resistance_support_lines, awesome_oscillator, momentum_oscillator,
    cluster_oscillators, relative_strength_indicator_rsi, full_stochastic, ultimate_oscillator,
    mov_avg_convergence_divergence, on_balance_volume, demand_index, bollinger_bands,
    triple_moving_average, moving_average_swing_trade, bear_bull_power, total_power,
    hull_moving_average, candlesticks, commodity_channel_index, rate_of_change_oscillator,
    know_sure_thing, average_true_range, average_directional_index, parabolic_sar
)

from libs.features import feature_detection_head_and_shoulders, analyze_price_gaps

from libs.functions.sub_functions.utils import (
    function_data_download, NORMAL, TICKER
)
from libs.functions.sub_functions.nasit import nasit_generation_function, ledger_function
from libs.functions.sub_functions.composites import (
    mci_function, tci_function, bci_function, correlation_index_function
)
from libs.functions.sub_functions.volatility_factor import vf_function
from libs.functions.sub_functions.outputs import (
    export_function, synopsis_function, assemble_last_signals_function, metadata_function,
    pptx_output_function, pdf_output_function
)
from libs.functions.sub_functions.misc import (
    relative_strength_function, risk_function
)


def run_function(config: dict, function_to_run: FunctionType, **kwargs):
    """run_functions

    Primary function that uses the function map to run all applicable functions

    Args:
        config (dict): configuration dictionary
        function_to_run (FunctionType): function referenced from the function map
    """
    data, fund_list = function_data_download(config)
    function_str = str(function_to_run.__name__).capitalize()
    for fund in fund_list:
        if fund != '^GSPC':
            print(f"{function_str} of {TICKER}{fund}{NORMAL}...")
            function_to_run(data[fund], plot_output=True, name=fund, **kwargs)


FUNCTION_MAP = {
    'mci': [mci_function],
    'bci': [bci_function],
    'tci': [tci_function],
    'trend': [run_function, get_trend_lines],
    'support_resistance': [run_function, find_resistance_support_lines],
    'clustered_oscs': [run_function, cluster_oscillators, {'function': 'all'}],
    'head_shoulders': [run_function, feature_detection_head_and_shoulders],
    'correlation': [correlation_index_function],
    'rsi': [
        run_function, relative_strength_indicator_rsi,
        {'out_suppress': False, 'trendlines': True}
    ],
    'stochastic': [run_function, full_stochastic, {"out_suppress": False}],
    'ultimate': [run_function, ultimate_oscillator, {"out_suppress": False}],
    'awesome': [run_function, awesome_oscillator],
    'momentum': [run_function, momentum_oscillator],
    'macd': [run_function, mov_avg_convergence_divergence],
    'relative_strength': [relative_strength_function],
    'obv': [run_function, on_balance_volume, {"trendlines": True}],
    'moving_average': [run_function, triple_moving_average],
    'swings': [run_function, moving_average_swing_trade],
    'hull': [run_function, hull_moving_average],
    'bear_bull': [run_function, bear_bull_power],
    'total_power': [run_function, total_power],
    'bollinger_bands': [run_function, bollinger_bands],
    'rate_of_change': [run_function, rate_of_change_oscillator],
    'know_sure_thing': [run_function, know_sure_thing],
    'gaps': [run_function, analyze_price_gaps],
    'candlestick': [run_function, candlesticks],
    'commodity': [run_function, commodity_channel_index],
    'average_true_range': [run_function, average_true_range],
    'adx': [run_function, average_directional_index],
    'parabolic_sar': [run_function, parabolic_sar],
    'demand_index': [run_function, demand_index],
    'alpha': [risk_function],
    'vf': [vf_function],
    'nasit_funds': [nasit_generation_function],
    'nf_now': [run_function, nasit_generation_function, {"print_only": True}, False],
    'ledger': [ledger_function],
    'synopsis': [synopsis_function],
    'last_signals':  [assemble_last_signals_function],
    'metadata': [metadata_function],
    'pptx': [pptx_output_function],
    'pdf': [pdf_output_function]
}


def only_functions_handler(config: dict):
    """ Main control function for functions """
    if config.get('run_functions') == ['nf']:
        print(f"Running {TICKER}NASIT{NORMAL} generation...")
    elif (config.get('run_functions') == ['tci']) or (config.get('run_functions') == ['bci']) \
            or (config.get('run_functions') == ['mci']):
        print(
            f"Running {TICKER}{config.get('run_functions')[0].upper()}{NORMAL}...")
    else:
        print(
            f"Running functions: {config['run_functions']} for {TICKER}{config['tickers']}{NORMAL}")

    if 'export' in config['run_functions']:
        # Non-dashed inputs will cause issues beyond export if not returning.
        export_function(config)
        return

    for function in config['run_functions']:
        functions = FUNCTION_MAP[function]
        if len(functions) == 1:
            # Typically a Composite index function
            functions[0](config)
        else:
            # Other functions. Default to kwargs is {}
            keyword_args = {}
            if len(functions) > 2:
                keyword_args = functions[2]
            if len(functions) == 4:
                functions[1](config, **keyword_args)
            else:
                functions[0](config, functions[1], **keyword_args)
