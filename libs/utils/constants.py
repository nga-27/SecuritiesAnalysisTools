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

SP500 = {
    "^GSPC": "S&P500"
}

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

EXEMPT_METRICS = [
    "metadata",
    "synopsis"
]
