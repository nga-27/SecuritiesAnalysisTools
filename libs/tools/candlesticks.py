import pandas as pd

from libs.utils import candlestick


def candlesticks(fund: pd.DataFrame, **kwargs) -> dict:

    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')
    view = kwargs.get('view', '')
    pbar = kwargs.get('progress_bar')

    candle = dict()

    if plot_output:
        candlestick(fund, title=name)
    else:
        filename = f"{name}/{view}/candlestick_{name}"
        candlestick(fund, title=name, filename=filename,
                    saveFig=True)
    return candle
