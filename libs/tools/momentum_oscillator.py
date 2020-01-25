import pandas as pd
import numpy as np

from libs.utils import ProgressBar


def momentum_oscillator(position: pd.DataFrame, **kwargs) -> dict:

    progress_bar = kwargs.get('progress_bar')

    mo = dict()

    if progress_bar is not None:
        progress_bar.uptick(increment=1.0)

    return mo
