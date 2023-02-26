""" PDF Title Generator """
import datetime

from fpdf import FPDF

from .pdf_utils import pdf_set_color_text, horizontal_spacer


def pdf_top_level_title_page(pdf: FPDF, **kwargs):
    """PDF Top Level Title Page

    Arguments:
        pdf {FPDF} -- pdf object

    Optional Args:
        version {str} -- (default: {"1.0.0"})

    Returns:
        FPDF -- pdf object
    """
    version = kwargs.get('version', "1.0.0")

    span = pdf.w - 2 * pdf.l_margin
    title = "Securities Analysis"
    sub_title = "A Technical Analysis of Financial Markets by 'nga-27'"
    generated = f"Generated: {datetime.datetime.now()}"
    version = f"Software Version: {version}"

    pdf.add_page()

    pdf.set_font("Arial", size=40)
    pdf.cell(span, 3.5, txt='', ln=1)

    pdf.set_font("Arial", size=40, style='B')
    pdf.cell(span, 0.5, txt=title, ln=1, align='C')

    pdf.set_font("Arial", size=12, style='I')
    pdf = pdf_set_color_text(pdf, "purple")
    pdf.cell(span, 0.4, txt=sub_title, ln=1, align='C')

    pdf = horizontal_spacer(pdf, 0.4)

    pdf.set_font("Arial", size=16)
    pdf = pdf_set_color_text(pdf, "green")
    pdf.cell(span, 0.3, txt=generated, ln=1, align='C')

    pdf.set_font("Arial", size=14)
    pdf = pdf_set_color_text(pdf, "green")
    pdf.cell(span, 0.3, txt=version, ln=1, align='C')

    return pdf
