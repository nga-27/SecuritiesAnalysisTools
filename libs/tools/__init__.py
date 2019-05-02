from .linear_regression import dual_plotting
from .linear_regression import lower_low, higher_high, bull_bear_th
from .linear_regression import trendline, trendline_deriv, local_minima
from .linear_regression import support, resistance
from .linear_regression import linear_regression

from .clusters import cluster_dates
from .trends import get_trend, get_trend_analysis
from .true_strength import basic_ratio, normalized_ratio, period_strength, get_SP500, is_fund_match 
from .moving_average import exponential_ma, windowed_ma_list

from .rsi import generate_rsi_signal, determine_rsi_swing_rejection
from .ultimate_oscillator import generate_ultimate_osc_signal, ult_osc_find_triggers, ult_osc_output
from .full_stochastic import generate_full_stoch_signal, get_full_stoch_features

from .trends import get_trend, get_trend_analysis
from .clusters import clustering, cluster_filtering, cluster_dates