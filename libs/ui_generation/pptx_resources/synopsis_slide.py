import os

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

from .slide_utils import pptx_ui_errors


def generate_synopsis_slide(slide, analysis: dict, fund: str, **kwargs):

    views = kwargs.get('views')
    if views is not None:
        return pptx_ui_errors(slide, "No 'views' object passed.")

    return slide
