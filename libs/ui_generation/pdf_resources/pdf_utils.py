""" PDF Utilities """
from fpdf import FPDF


color_to_rgb_ARRAY = {
    'black': [0x00, 0x00, 0x00],
    'blue': [0x00, 0x00, 0xFF],
    'green': [0x00, 0xCC, 0x00],
    'purple': [0x7F, 0x00, 0xFF],
    'yellow': [0xee, 0xd4, 0x00],
    'orange': [0xff, 0x99, 0x33],
    'red': [0xff, 0x00, 0x00]
}

def pdf_set_color_text(pdf: FPDF, color: str):
    """PDF Set Text Color

    Arguments:
        pdf {FPDF} -- pdf object
        color {str} -- one of the RGB_arry colors

    Returns:
        FPDF -- pdf object
    """
    color = color_to_rgb_ARRAY.get(color, [0x00, 0x00, 0x00])
    pdf.set_text_color(color[0], color[1], color[2])
    return pdf


def horizontal_spacer(pdf, height: float):
    """ Wrapper to create a horizontal line spacing """
    pdf.ln(height)
    return pdf
