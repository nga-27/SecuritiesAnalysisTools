import datetime

import fpdf  # pylint: disable=F0401
from fpdf import FPDF  # pylint: disable=F0401

from .pdf_utils import color_to_RGB_array, horizontal_spacer
from .pdf_utils import PDF_CONSTS


SPAN = PDF_CONSTS["span"]


def pdf_top_level_title_page(pdf, **kwargs):

    version = kwargs.get('version', "0.1.28")

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
    color = color_to_RGB_array('purple')
    pdf.set_text_color(color[0], color[1], color[2])
    pdf.cell(SPAN, 0.4, txt=SUB_TITLE, ln=1, align='C')

    pdf = horizontal_spacer(pdf, 0.4)

    pdf.set_font("Arial", size=16)
    color = color_to_RGB_array('green')
    pdf.set_text_color(color[0], color[1], color[2])
    pdf.cell(SPAN, 0.3, txt=GENERATED, ln=1, align='C')

    pdf.set_font("Arial", size=14)
    color = color_to_RGB_array('green')
    pdf.set_text_color(color[0], color[1], color[2])
    pdf.cell(SPAN, 0.3, txt=VERSION, ln=1, align='C')

    return pdf
