""" Resource group for item-specific (or utility-based) pptx content generation """
from .title_slide import create_presentation_title
from .slide_utils import (
    subtitle_header, intro_slide, slide_title_header, COLOR_TO_RGB, space_injector
)
from .ci_slides import make_mci_slides, make_bci_slides, make_cci_slides, make_tci_slides
from .fund_slides import make_fund_slides
