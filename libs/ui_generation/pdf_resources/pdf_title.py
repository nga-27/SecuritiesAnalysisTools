import datetime

import fpdf  # pylint: disable=F0401
from fpdf import FPDF  # pylint: disable=F0401

from .pdf_utils import pdf_set_color_text, horizontal_spacer
from .pdf_utils import PDF_CONSTS


def pdf_top_level_title_page(pdf, **kwargs):
    """PDF Top Level Title Page

    Arguments:
        pdf {FPDF} -- pdf object

    Optional Args:
        version {str} -- (default: {"0.1.28"})

    Returns:
        FPDF -- pdf object
    """
    version = kwargs.get('version', "0.1.28")

    SPAN = pdf.w - 2 * pdf.l_margin
    TITLE = "Securities Analysis"
    SUB_TITLE = "A Technical Analysis of Financial Markets by 'nga-27'"
    GENERATED = f"Generated: {datetime.datetime.now()}"
    VERSION = f"Software Version: {version}"

    pdf.add_page()

    pdf.set_font("Arial", size=40)
    pdf.cell(SPAN, 3.5, txt='', ln=1)

    pdf.set_font("Arial", size=40, style='B')
    pdf.cell(SPAN, 0.5, txt=TITLE, ln=1, align='C')

    pdf.set_font("Arial", size=12, style='I')
    pdf = pdf_set_color_text(pdf, "purple")
    pdf.cell(SPAN, 0.4, txt=SUB_TITLE, ln=1, align='C')

    pdf = horizontal_spacer(pdf, 0.4)

    pdf.set_font("Arial", size=16)
    pdf = pdf_set_color_text(pdf, "green")
    pdf.cell(SPAN, 0.3, txt=GENERATED, ln=1, align='C')

    pdf.set_font("Arial", size=14)
    pdf = pdf_set_color_text(pdf, "green")
    pdf.cell(SPAN, 0.3, txt=VERSION, ln=1, align='C')

    return pdf
