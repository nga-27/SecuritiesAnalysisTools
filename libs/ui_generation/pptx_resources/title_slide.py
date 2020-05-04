from datetime import datetime
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN  # pylint: disable=no-name-in-module

# Slide Layouts
PRES_TITLE_SLIDE = 0
TITLE_CONTENT_SLIDE = 1
SECTION_HEADER_SLIDE = 2
TWO_CONTENT_SLIDE = 3
COMPARISON_SLIDE = 4
TITLE_ONLY_SLIDE = 5
BLANK_SLIDE = 6
CONTENT_W_CAPTION_SLIDE = 7
PICTURE_W_CAPTION_SLIDE = 8


def title_presentation(prs, year: str, VERSION: str, **kwargs):
    """Title Slide

    Arguments:
        prs {pptx-obj} -- powerpoint python object
        year {str} -- '2020', for exampe
        VERSION {str} -- '0.2.02', for example

    Returns:
        pptx-obj -- powerpoint object
    """
    height = prs.slide_height
    width = int(16 * height / 9)
    prs.slide_width = width
    slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])

    LEFT_INCHES = 6
    left = Inches(LEFT_INCHES)
    top = Inches(2.45)
    text = slide.shapes.add_textbox(left, top, Inches(1), Inches(1))
    text_frame = text.text_frame

    p = text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = f'Securities Analysis'
    p.font.bold = True
    p.font.size = Pt(48)
    p.font.name = 'Arial'

    p4 = text_frame.add_paragraph()
    p4.alignment = PP_ALIGN.CENTER
    p4.text = f"A Technical Analysis of Financial Markets by 'nga-27'"
    p4.font.italic = True
    p4.font.size = Pt(14)
    p4.font.color.rgb = RGBColor(0x74, 0x3c, 0xe6)
    p4.font.name = 'Arial'

    left = Inches(LEFT_INCHES)
    top = Inches(4.0)
    text = slide.shapes.add_textbox(left, top, Inches(1), Inches(1))
    text_frame2 = text.text_frame

    p2 = text_frame2.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    p2.text = f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    p2.font.bold = False
    p2.font.size = Pt(22)
    p2.font.color.rgb = RGBColor(0x30, 0x9c, 0x4f)
    p2.font.name = 'Arial'

    p3 = text_frame2.add_paragraph()
    p3.alignment = PP_ALIGN.CENTER
    p3.text = f'Software Version: {VERSION}'
    p3.font.bold = False
    p3.font.size = Pt(18)
    p3.font.color.rgb = RGBColor(0x30, 0x9c, 0x4f)
    p3.font.name = 'Arial'

    return prs
