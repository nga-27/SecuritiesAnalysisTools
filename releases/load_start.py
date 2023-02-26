""" load_start - The initial function that builds the start screen """
from typing import Tuple, Union, List

from libs.utils import (
    download_data_all, has_critical_error, index_appender, remove_temp_dir, configure_temp_dir,
    TEXT_COLOR_MAP
)
from libs.functions import only_functions_handler


PROCESS_STEPS_PROD = 30

HEADER_COLOR = TEXT_COLOR_MAP["blue"]
PROD_COLOR = TEXT_COLOR_MAP["green"]
NORMAL_COLOR = TEXT_COLOR_MAP["white"]


def init_script(config: dict) -> Tuple[
    Union[dict, None], Union[List[str], None], Union[List[str], None], Union[dict, None]]:
    """Init Script

    Arguments:
        config {dict} -- startup config object to control application

    Returns:
        list -- script: dataset, funds, periods, config
    """
    config['process_steps'] = PROCESS_STEPS_PROD
    if config['state'] == 'halt':
        return None, None, None, None

    if 'function' in config['state']:
        # If only simple functions are desired, they go into this handler
        only_functions_handler(config)
        return None, None, None, None

    if 'no_index' not in config['state']:
        config['tickers'] = index_appender(config['tickers'])
        config['process_steps'] = config['process_steps'] + 2

    if 'debug' in config['state']:
        print(
            f"{HEADER_COLOR}~~~~ DEBUG MODE ENABLED ~~~~ {NORMAL_COLOR}")

    # Temporary directories to save graphs as images, etc.
    remove_temp_dir()
    configure_temp_dir()

    dataset, funds, periods, config = download_data_all(config=config)

    for _, data in dataset.items():
        if has_critical_error(data, 'download_data'):
            return None, None, None, None

    return dataset, funds, periods, config
