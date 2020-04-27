def assemble_last_signals(meta_sub: dict, lookback: int = 5, **kwargs) -> dict:
    """assemble_last signals

    Look through all indicators of lookback time and list them

    Arguments:
        meta_sub {dict} -- metadata subset "metadata[fund][view]"

    Keyword Arguments:
        lookback {int} -- number of trading periods into past to find signals (default: {5})

    Returns:
        dict -- last signals data object
    """
    pbar = kwargs.get('progress_bar')

    return {}
