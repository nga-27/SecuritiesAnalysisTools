TEXT_COLOR_MAP = {
    "black": "\033[0;30m",
    "red": "\033[0;31m",
    "green": "\033[0;32m",
    "yellow": "\033[0;33m",
    "blue": "\033[0;34m",
    "purple": "\033[0;35m",
    "cyan": "\033[0;36m",
    "white": "\033[0;37m",

    "blue_bold": "\033[1;34m",
    "green_bold": "\033[1;32m",
    "purple_bold": "\033[1;35m",
}

INDEXES = {
    "^GSPC": "S&P500",
    "^IRX": "3MO-TBILL"
}

SKIP_INDEXES = [
    "^IRX"
]

STANDARD_COLORS = {
    "warning": TEXT_COLOR_MAP["yellow"],
    "error": TEXT_COLOR_MAP["red"],
    "normal": TEXT_COLOR_MAP["white"],
    "ticker": TEXT_COLOR_MAP["cyan"]
}

LOGO_COLORS = {
    "main": TEXT_COLOR_MAP["purple_bold"],
    "other": TEXT_COLOR_MAP["blue_bold"],
    "copywrite": TEXT_COLOR_MAP["green_bold"]
}

TREND_COLORS = {
    "good": TEXT_COLOR_MAP["green"],
    "hold": TEXT_COLOR_MAP["yellow"],
    "bad": TEXT_COLOR_MAP["red"]
}

PRINT_CONSTANTS = {
    "return_same_line": "\033[F"
}

EXEMPT_METRICS = [
    "metadata",
    "synopsis"
]

INDICATOR_NAMES = [
    "clustered_osc",
    "full_stochastic",
    "rsi",
    "ultimate",
    "awesome",
    "momentum_oscillator",
    "on_balance_volume",
    "moving_average",
    "exp_moving_average",
    "sma_swing_trade",
    "ema_swing_trade",
    "hull_moving_average",
    "macd",
    "candlesticks",
    "bear_bull_power",
    "total_power",
    "bollinger_bands",
    "commodity_channels"
]
