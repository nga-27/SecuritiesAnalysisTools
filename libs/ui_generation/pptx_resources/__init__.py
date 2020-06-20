""" Resource group for item-specific (or utility-based) pptx content generation """
from .title_slide import title_presentation
from .slide_utils import subtitle_header, intro_slide, slide_title_header
from .slide_utils import color_to_RGB, space_injector
from .ci_slides import make_MCI_slides, make_BCI_slides, make_CCI_slides, make_TCI_slides
from .fund_slides import make_fund_slides
