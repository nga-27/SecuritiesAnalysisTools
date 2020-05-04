import os
import datetime

from pptx import Presentation

from libs.ui_generation.pptx_resources import title_presentation
from libs.ui_generation.pptx_resources import intro_slide
from libs.ui_generation.pptx_resources import make_BCI_slides, make_MCI_slides
from libs.ui_generation.pptx_resources import make_CCI_slides, make_TCI_slides
from libs.ui_generation.pptx_resources import make_fund_slides
from libs.utils import TEXT_COLOR_MAP, STANDARD_COLORS

PPTX_NAME_COLOR = TEXT_COLOR_MAP["purple"]

NORMAL = STANDARD_COLORS["normal"]
ERROR = STANDARD_COLORS["error"]
WARNING = STANDARD_COLORS["warning"]


def slide_creator(analysis: dict, **kwargs):
    """Powerpoint Creator

    High-level function for converting inventors spreadsheet to slides

    Arguments:
        analysis {dict} -- data obj with all analysis data

    Optional Args:
        year {str} -- '2001', for example (default: {None})
        version {str} -- '0.1.20', for example (default: {None})
        config {dict} -- main control obj (default: {None})
    """

    year = kwargs.get('year')
    version = kwargs.get('version', "0.2.02")
    config = kwargs.get('config')

    if year is None:
        year = datetime.datetime.now().strftime("%Y")

    if 'suppress_pptx' not in config['state']:
        print("")
        print("Starting presentation creation.")
        if config is not None:
            year = config.get('date_release', '').split('-')[0]
            version = config.get('version')
            views = config.get('views', {}).get('pptx', '2y')

        else:
            year = year
            version = version
            views = '2y'

        try:
            prs = Presentation()

            prs = title_presentation(prs, year, VERSION=version)
            prs = intro_slide(prs)
            prs = make_MCI_slides(prs, analysis.get('_METRICS_', {}))
            prs = make_CCI_slides(prs)
            prs = make_BCI_slides(prs)
            prs = make_TCI_slides(prs)
            prs = make_fund_slides(prs, analysis, views=views)

            out_dir = "output"
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)

            title = f"Financial Analysis {year}.pptx"
            filename = os.path.join(out_dir, title)
            prs.save(filename)

            print(
                f"Presentation '{PPTX_NAME_COLOR}{title}{NORMAL}' created.")

        except:
            print(f"{WARNING}Presentation failed to be created.{NORMAL}")
