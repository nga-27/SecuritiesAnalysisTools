""" pdf generator """
import os
import datetime

from fpdf import FPDF

from libs.utils import STANDARD_COLORS

from libs.ui_generation.pdf_resources import (
    pdf_top_level_title_page, fund_pdf_pages
)

WARNING = STANDARD_COLORS["warning"]
NORMAL = STANDARD_COLORS["normal"]


def create_pdf(analysis: dict, debug: bool = False, **kwargs):
    """PDF Creator

    Creates a subset of metrics, items into a pdf report.

    Arguments:
        analysis {dict} -- data run object

    Optional Args:
        year {str} -- (default: {None})
        version {str} -- (default: {"0.1.28"})
        config {dict} -- (default: {None})
    """
    year = kwargs.get('year')
    version = kwargs.get('version', "0.2.02")
    config = kwargs.get('config')

    if year is None:
        year = datetime.datetime.now().strftime("%Y")

    if not debug and config is not None:
        if 'debug' in config.get('state', ''):
            debug = True

    output_file_name = os.path.join("output", f"Financial_Analysis_{year}.pdf")

    print("")
    print("Starting metrics PDF creation.")
    views = '2y'
    if config is not None:
        year = config.get('date_release', '').split('-')[0]
        version = config.get('version')
        views = config.get('views', {}).get('pptx', '2y')

    if debug:
        pdf = FPDF(unit='in', format='letter')
        pdf = pdf_top_level_title_page(pdf, version=version)
        pdf = fund_pdf_pages(pdf, analysis, views=views)

        pdf.output(output_file_name)

    else:
        try:
            pdf = FPDF(unit='in', format='letter')
            pdf = pdf_top_level_title_page(pdf, version=version)
            pdf = fund_pdf_pages(pdf, analysis, views=views)

            pdf.output(output_file_name)

        except: # pylint: disable=bare-except
            print(f"{WARNING}PDF failed to be created.{NORMAL}")
