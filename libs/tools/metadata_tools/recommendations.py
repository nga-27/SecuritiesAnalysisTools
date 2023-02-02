""" Recommendations """
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

import numpy as np
import yfinance as yf

from libs.utils.plotting import generic_plotting


def get_recommendations(ticker: yf.Ticker) -> dict:
    """Get Recommendations

    Arguments:
        ticker {yf-object} -- current yf Ticker object
        st {yf-object} -- ticker object from yfinance (0.1.50)

    Returns:
        dict -- Recommendations data object
    """
    recommendations = {}

    try:
        t_recommend = ticker.recommendations
        recommendations['dates'] = [date.strftime('%Y-%m-%d') for date in t_recommend.index]
        recommendations['firms'] = list(t_recommend['Firm'])
        recommendations['grades'] = list(t_recommend['To Grade'])
        recommendations['actions'] = list(t_recommend['Action'])
    except: # pylint: disable=bare-except
        recommendations = {'dates': [], 'firms': [], 'grades': [], 'actions': []}

    return recommendations


def calculate_recommendation_curve(recoms: dict, **kwargs) -> dict:
    """Calculate Recommendation Curve

    Arguments:
        recoms {dict} -- recommendation data object

    Returns:
        dict -- recommendation curve data object
    """
    # pylint: disable=too-many-locals
    plot_output = kwargs.get('plot_output', True)
    name = kwargs.get('name', '')

    tabular = {}
    tabular['dates'] = []
    tabular['grades'] = []

    if len(recoms['dates']) > 0:
        firms = {}
        dates = []
        grades = []
        dates_x = recoms.get('dates', [])
        grades_x = grade_to_number(recoms.get('grades', []))
        firms_x = recoms.get('firms', [])

        i = 0
        while i < len(dates_x):
            date = dates_x[i]
            dates.append(date)
            while (i < len(dates_x)) and (date == dates_x[i]):
                firms[firms_x[i]] = {}
                firms[firms_x[i]]['grade'] = grades_x[i]
                firms[firms_x[i]]['date'] = date
                i += 1
            firms = prune_ratings(firms, date)
            sum_ = [value['grade'] for _, value in firms.items()]
            grades.append(np.mean(sum_))

        tabular['grades'] = grades
        tabular['dates'] = dates

        x_vals = [datetime.strptime(date, "%Y-%m-%d") for date in tabular['dates']]

        if plot_output:
            generic_plotting([tabular['grades']], x=x_vals, title="Ratings by Firms",
                             ylabel="Ratings (Proportional 0 - 4)")

        else:
            filename = os.path.join(name, f"grades_{name}.png")
            generic_plotting([tabular['grades']], x=x_vals, title="Ratings by Firms",
                             ylabel="Ratings (Proportional 0 - 4)",
                             save_fig=True, filename=filename)

    return tabular


def grade_to_number(grades: list) -> list:
    """Grade to Number

    Arguments:
        grades {list} -- list of recommendation grades (strings)

    Returns:
        list -- list of grades (floats)
    """
    grade_keys = {
        "Strong Buy": 4.0,
        "Buy": 3.0,
        "Overweight": 3.0,
        "Outperform": 3.0,
        "Neutral": 2.0,
        "Hold": 2.0,
        "Market Perform": 2.0,
        "Equal-Weight": 2.0,
        "Sector Perform": 2.0,
        "Underperform": 1.0,
        "Underweight": 1.0,
        "Sell": 0.0
    }

    val_grad = []
    for grade in grades:
        val_grad.append(grade_keys.get(grade, 3.0))
    return val_grad


def prune_ratings(firms: dict, date: str) -> dict:
    """Prune Ratings

    To keep ratings fresh, eliminate old ratings (beyond 2 years from 'date')

    Arguments:
        firms {dict} -- firm data object (from recommendation curve)
        date {str} -- specific point in time to add 2 years to

    Returns:
        dict -- pruned firm list
    """
    time_stamp = datetime.strptime(date, '%Y-%m-%d')
    for firm in list(firms):
        time_stamp2 = datetime.strptime(firms[firm]['date'], '%Y-%m-%d')
        time_stamp2 = time_stamp2 + relativedelta(years=2)
        if time_stamp > time_stamp2:
            firms.pop(firm)

    return firms
