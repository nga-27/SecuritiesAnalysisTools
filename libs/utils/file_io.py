import os
import shutil
import glob


def configure_temp_dir():
    """ Configure Temporary Directory """
    output_dir = "output"
    out_path = os.path.join(output_dir, "temp")
    if not os.path.exists(out_path):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        os.mkdir(out_path)


def remove_temp_dir():
    """ Remove Temporary Directory """
    out_path = os.path.join("output", "temp")
    if os.path.exists(out_path):
        shutil.rmtree(out_path)


def create_sub_temp_dir(name: str, sub_periods=[]):
    """Create Sub Temporary Directory

    Arguments:
        name {str} -- name of sub directory, usually a fund name

    Keyword Arguments:
        sub_periods {list} -- list of fund periods, or "views" (default: {[]})
    """
    out_path = os.path.join("output", "temp")
    fund_path = os.path.join(out_path, name)
    if not os.path.exists(fund_path):
        os.mkdir(fund_path)

    if len(sub_periods) > 0:
        for period in sub_periods:
            period_path = os.path.join(fund_path, period)
            if not os.path.exists(period_path):
                os.mkdir(period_path)
