import json
import os

from libs.metrics import (
    metadata_to_dataset, generate_synopsis, assemble_last_signals
)
from libs.ui_generation import slide_creator, PDF_creator
from libs.tools import get_api_metadata

from .utils import (
    WARNING, NORMAL, TEXT_COLOR_MAP, function_data_download
)


def export_function(config: dict):
    metadata_to_dataset(config)


def synopsis_function(_: dict):
    meta_file = os.path.join("output", "metadata.json")
    if not os.path.exists(meta_file):
        print(
            f"{WARNING}Warning: '{meta_file}' file does not exist. Run main program.{NORMAL}")
        return

    with open(meta_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()

        for fund in m_data:
            if fund != '_METRICS_':
                print("")
                synopsis = generate_synopsis(m_data, name=fund, print_out=True)
                print("")
                if synopsis is None:
                    print(f"{WARNING}Warning: key 'synopsis' not present.{NORMAL}")
                    return


def assemble_last_signals_function(_: dict):
    meta_file = os.path.join("output", "metadata.json")
    if not os.path.exists(meta_file):
        print(
            f"{WARNING}Warning: '{meta_file}' file does not exist. Run main program.{NORMAL}")
        return

    with open(meta_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()

        for fund in m_data:
            if fund != '_METRICS_':
                print("")
                assemble_last_signals(
                    m_data[fund], standalone=True, print_out=True, name=fund)
                print("")


def metadata_function(config: dict):
    print(f"Getting Metadata for funds...")
    print(f"")
    _, fund_list = function_data_download(config, fund_list_only=True)
    for fund in fund_list:
        if fund != '^GSPC':
            metadata = get_api_metadata(fund, plot_output=True)
            altman_z = metadata.get('altman_z', {})
            color = TEXT_COLOR_MAP[altman_z.get('color', 'white')]
            print("\r\n")
            print(f"Altman-Z Score: {color}{altman_z.get('score', 'n/a')}{NORMAL}")
            print("\r\n")


def pptx_output_function(config: dict):
    meta_file = os.path.join("output", "metadata.json")
    if not os.path.exists(meta_file):
        print(
            f"{WARNING}Warning: '{meta_file}' file does not exist. Run main program.{NORMAL}")
        return

    with open(meta_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()

        t_fund = None
        for fund in m_data:
            if fund != '_METRICS_':
                t_fund = fund

        if t_fund is None:
            print(
                f"{WARNING}No valid fund found for 'pptx_output_function'. Exiting...{NORMAL}")
            return

        if '2y' not in m_data[t_fund]:
            for period in m_data[t_fund]:
                if (period != 'metadata') and (period != 'synopsis'):
                    config['views']['pptx'] = period

        slide_creator(m_data, config=config)
        return


def pdf_output_function(config: dict):
    meta_file = os.path.join("output", "metadata.json")
    if not os.path.exists(meta_file):
        print(
            f"{WARNING}Warning: '{meta_file}' file does not exist. Run main program.{NORMAL}")
        return

    with open(meta_file) as m_file:
        m_data = json.load(m_file)
        m_file.close()

        t_fund = None
        for fund in m_data:
            if fund != '_METRICS_':
                t_fund = fund

        if t_fund is None:
            print(
                f"{WARNING}No valid fund found for 'pptx_output_function'. Exiting...{NORMAL}")
            return

        if '2y' not in m_data[t_fund]:
            for period in m_data[t_fund]:
                if (period != 'metadata') and (period != 'synopsis'):
                    config['views']['pptx'] = period

        PDF_creator(m_data, config=config)
        return