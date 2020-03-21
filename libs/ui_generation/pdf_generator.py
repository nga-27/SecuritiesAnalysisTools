import datetime

from fpdf import FPDF  # pylint: disable=F0401

from libs.ui_generation.pdf_resources import pdf_top_level_title_page
from libs.ui_generation.pdf_resources import fund_pdf_pages


def PDF_creator(analysis: dict, **kwargs):
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
    version = kwargs.get('version', "0.1.28")
    config = kwargs.get('config')

    if year is None:
        year = datetime.datetime.now().strftime("%Y")

    OUTFILE_NAME = f"output/Financial_Analysis_{year}.pdf"

    print("")
    print("Starting metrics PDF creation.")
    if config is not None:
        year = config.get('date_release', '').split('-')[0]
        version = config.get('version')
        views = config.get('views', {}).get('pptx', '2y')
    else:
        year = year
        version = version
        views = '2y'

    pdf = FPDF(unit='in', format='letter')
    pdf = pdf_top_level_title_page(pdf, version=version)
    pdf = fund_pdf_pages(pdf, analysis, views=views)

    pdf.output(OUTFILE_NAME)
