import datetime

import fpdf  # pylint: disable=F0401
from fpdf import FPDF  # pylint: disable=F0401

from libs.utils import SP500

from .pdf_utils import color_to_RGB_array, horizontal_spacer
from .pdf_utils import PDF_CONSTS


SPAN = PDF_CONSTS["span"]


def fund_pdf_pages(pdf, analysis: dict, **kwargs):

    views = kwargs.get('views')

    has_view = False
    if views is None:
        for fund in analysis:
            for period in analysis[fund]:
                views = period
                has_view = True
                break
            if has_view:
                break

    for fund in analysis:
        if fund != '_METRICS_':
            name = SP500.get(fund, fund)

            pdf.add_page()
            pdf.set_font("Arial", size=36, style='B')
            pdf.cell(SPAN, 0.8, txt='', ln=1)
            color = color_to_RGB_array('black')
            pdf.set_text_color(color[0], color[1], color[2])
            pdf.cell(SPAN, 1, txt=name, ln=1, align='C')

    return pdf
