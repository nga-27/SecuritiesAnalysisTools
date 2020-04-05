from libs.utils import start_header
from libs.utils import download_data_all
from libs.utils import has_critical_error
from libs.utils import index_appender
from libs.utils import remove_temp_dir, configure_temp_dir
from libs.functions import only_functions_handler
from libs.utils import TEXT_COLOR_MAP


################################
_DEV_VERSION_ = '0.2.1'
_DATE_REVISION_DEV_ = '2020-04-04'
################################
PROCESS_STEPS_DEV = 23
PROCESS_STEPS_PROD = 23

HEADER_COLOR = TEXT_COLOR_MAP["blue"]
PROD_COLOR = TEXT_COLOR_MAP["green"]
NORMAL_COLOR = TEXT_COLOR_MAP["white"]


def init_script(config: dict, **kwargs) -> list:
    """Init Script

    Arguments:
        config {dict} -- startup config object to control application

    Optional Args:
        release {str} -- 'dev' or 'prod' (default: {'prod'})

    Returns:
        list -- script: dataset, funds, periods, config
    """
    release = kwargs.get('release', 'prod')

    if release == 'dev':
        config['process_steps'] = PROCESS_STEPS_DEV
    elif release == 'prod':
        config['process_steps'] = PROCESS_STEPS_PROD

    if config['release'] == True:
        # Use only after release!
        print(" ")

        if release == 'dev':
            print(
                f"{HEADER_COLOR}~~~~ DEVELOPMENT VERSION ~~~~ [latest functionality, 'unclean' version]{NORMAL_COLOR}")

            config = start_header(update_release=_DATE_REVISION_DEV_,
                                  version=_DEV_VERSION_, options=True)
            config['process_steps'] = PROCESS_STEPS_DEV

    else:
        if release == 'prod':
            print(
                f"{PROD_COLOR}~~~~ PRODUCTION ENVIRONMENT ~~~~{NORMAL_COLOR}")
            print(" ")

    if config['state'] == 'halt':
        return

    if 'function' in config['state']:
        # If only simple functions are desired, they go into this handler
        only_functions_handler(config)
        return

    if 'no_index' not in config['state']:
        config['tickers'] = index_appender(config['tickers'])
        config['process_steps'] = config['process_steps'] + 2

    # Temporary directories to save graphs as images, etc.
    remove_temp_dir()
    configure_temp_dir()

    dataset, funds, periods, config = download_data_all(config=config)

    for period in dataset:
        e_check = {'tickers': config['tickers']}
        if has_critical_error(dataset[period], 'download_data', misc=e_check):
            return None

    return dataset, funds, periods, config
