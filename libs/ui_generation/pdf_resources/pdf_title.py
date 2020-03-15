import fpdf  # pylint: disable=F0401
from fpdf import FPDF  # pylint: disable=F0401


def pdf_top_level_title_page(pdf):

    TITLE = "Financial Analysis Tools"
    pdf.add_page()
    pdf.set_font("Arial", size=40, style='B')
    pdf.cell(8, 1, txt=TITLE, ln=1, align='C')

    return pdf
