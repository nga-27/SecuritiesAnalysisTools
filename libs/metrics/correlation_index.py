import os
import json
import numpy as np
from datetime import datetime, timedelta

from libs.utils import download_data_indexes, index_appender, ProgressBar
from libs.utils import dual_plotting
from libs.tools import beta_comparison_list, simple_moving_avg


def correlation_composite_index(config: dict, **kwargs) -> dict:
    """Correlation Composite Index (CCI)

    Arguments:
        config {dict} -- controlling config dictionary

    Optional Args:
        plot_output {bool} -- (default: {True})
        clock {uint64_t} -- time for prog_bar (default: {None})
        data {pd.DataFrame} -- funds data object (default: {None})
        sectors {list} -- sectors list (default: {None})

    Returns:
        list -- dict contains all correlation items, data, sectors list
    """
    plot_output = kwargs.get('plot_output', True)
    clock = kwargs.get('clock')
    data = kwargs.get('data')
    sectors = kwargs.get('sectors')

    corr = dict()
    corr_config = config.get('properties', {}).get(
        'Indexes', {}).get('Correlation', {})

    if corr_config.get('run', False):
        config['duration'] = corr_config.get('type', 'long')

        if data is None or sectors is None:
            data, sectors = metrics_initializer(config['duration'])
        if data:
            corr = get_correlation(
                data, sectors, plot_output=plot_output, clock=clock)

    return corr, data, sectors


def metrics_initializer(duration: str = 'short') -> list:
    """Metrics Initializer

    Keyword Arguments:
        duration {str} -- duration of view (default: {'short'})

    Returns:
        list -- data downloaded and sector list
    """
    metrics_file = os.path.join("resources", "sectors.json")
    if not os.path.exists(metrics_file):
        return None, []

    with open(metrics_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()
        m_data = m_data.get("Correlation")

    sectors = m_data['tickers']
    tickers = " ".join(m_data['tickers'])
    START = m_data['start']

    tickers = index_appender(tickers)
    all_tickers = tickers.split(' ')
    date = datetime.now().strftime('%Y-%m-%d')

    print(" ")
    print('Fetching Correlation Composite Index funds...')

    if duration == 'short':
        START = datetime.today() - timedelta(days=900)
        START = START.strftime('%Y-%m-%d')

    data, _ = download_data_indexes(
        indexes=all_tickers, tickers=tickers, start=START, end=date, interval='1d')
    print(" ")

    return data, sectors


def get_correlation(data: dict, sectors: list, **kwargs) -> dict:
    """Get Correlation

    Arguments:
        data {dict} -- downloaded data
        sectors {list} -- sector list

    Optional Arguments:
        plot_output {bool} -- (default: {True})
        clock {uint64_t} -- time for prog_bar (default: {None})

    Returns:
        dict -- object with correlations
    """
    plot_output = kwargs.get('plot_output', True)
    clock = kwargs.get('clock')

    PERIOD_LENGTH = [100, 50, 25]
    WEIGHTS = [1.5, 1.25, 1.0]
    corr_data = dict()

    if '^GSPC' in data.keys():
        tot_len = len(data['^GSPC']['Close'])
        start_pt = max(PERIOD_LENGTH)

        tot_count = (tot_len - start_pt) * 11 * len(PERIOD_LENGTH)
        if tot_count < 25000:
            divisor = 50
        else:
            divisor = 250
        pbar_count = np.ceil(tot_count / float(divisor))

        progress_bar = ProgressBar(
            pbar_count, name="Correlation Composite Index", offset=clock)
        progress_bar.start()

        corrs = {}
        dates = data['^GSPC'].index[start_pt:tot_len]
        net_correlation = []
        legend = []
        counter = 0

        for period in PERIOD_LENGTH:
            nc = [0.0] * (tot_len-start_pt)

            for sector in sectors:
                corrs[sector] = []

                for i in range(start_pt, tot_len):
                    _, rsqd = beta_comparison_list(
                        data[sector]['Close'][i-period:i], data['^GSPC']['Close'][i-period:i])
                    corrs[sector].append(rsqd)
                    nc[i-start_pt] += rsqd
                    counter += 1

                    if counter == divisor:
                        progress_bar.uptick()
                        counter = 0

            net_correlation.append(nc.copy())
            legend.append('Corr-' + str(period))

        norm_corr = []
        for nc_period in net_correlation:
            max_ = np.max(nc_period)
            norm = [x / max_ for x in nc_period]
            norm_corr.append(norm)

        net_correlation = norm_corr.copy()

        dual_plotting(net_correlation,
                      data['^GSPC']['Close'][start_pt:tot_len],
                      x=dates,
                      y1_label=legend,
                      y2_label='S&P500',
                      title='CCI Net Correlation',
                      saveFig=(not plot_output),
                      filename='CCI_net_correlation.png')

        str_dates = []
        for date in dates:
            str_dates.append(date.strftime("%Y-%m-%d"))

        corr_data['tabular'] = {}
        for i, nc_period in enumerate(net_correlation):
            corr_data[legend[i]] = {}
            corr_data[legend[i]]['data'] = nc_period.copy()
            corr_data[legend[i]]['date'] = str_dates.copy()
            corr_data['tabular'][legend[i]] = nc_period.copy()

        corr_data['tabular']['date'] = str_dates.copy()

        overall_signal = [0.0] * len(corr_data['tabular']['date'])
        for i, period in enumerate(PERIOD_LENGTH):
            string = f"Corr-{period}"
            corr_signal = corr_data['tabular'].get(string, [])
            if len(corr_signal) > 0:
                weight = WEIGHTS[i]
                for j, csl in enumerate(corr_signal):
                    overall_signal[j] += csl * weight

        signal_line = simple_moving_avg(overall_signal, 20, data_type='list')

        dual_plotting(data['^GSPC']['Close'][start_pt:tot_len],
                      [overall_signal, signal_line],
                      x=dates,
                      y1_label='S&P500',
                      y2_label=['Overall Signal', '20d-SMA'],
                      title='Overall Correlation Signal',
                      saveFig=(not plot_output),
                      filename='CCI_overall_correlation.png')

        diff_signal = [x - signal_line[i]
                       for i, x in enumerate(overall_signal)]
        dual_plotting(data['^GSPC']['Close'][start_pt:tot_len],
                      diff_signal,
                      x=dates,
                      y1_label='S&P500',
                      y2_label='Corr - Signal Line',
                      title='Diff Correlation Signal',
                      saveFig=(not plot_output),
                      filename='CCI_diff_correlation.png')

        corr_data['tabular']['overall'] = overall_signal
        corr_data['tabular']['signal_line'] = signal_line
        corr_data['tabular']['diff_signal'] = diff_signal

        progress_bar.end()

    return corr_data
