""" Earnings Per Share """
import numpy as np


def calculate_eps(meta: dict) -> dict:
    """Calculate Earnings Per Share

    Arguments:
        meta {dict} -- metadata object

    Returns:
        dict -- EPS data object
    """
    eps = {}
    q_earnings = meta.get('earnings', {}).get('quarterly')
    shares = meta.get('info', {}).get('sharesOutstanding')

    if shares and q_earnings:
        eps['period'] = []
        eps['eps'] = []
        for i, earn in enumerate(q_earnings['earnings']):
            eps['period'].append(q_earnings['period'][i])
            eps['eps'].append(np.round(earn / shares, 3))

    return eps
