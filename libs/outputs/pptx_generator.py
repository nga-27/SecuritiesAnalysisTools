from pptx import Presentation
from pptx.util import Inches, Pt
import pandas as pd 
import numpy as np 
from datetime import datetime
import os 

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


def title_presentation(year: str):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[PRES_TITLE_SLIDE])
    title = slide.shapes.title
    title.text = f'Financial Analysis'
    stitle = slide.placeholders[1]
    stitle.text = f'Generated: {datetime.now()}'

    return prs 


def template_3M(prs):
    """ takes in a Presentation object and applies 3M footer on slides """

    for slide in range(len(prs.slides)):
        left = Inches(0.1)
        top = Inches(7.25)
        height = Inches(.24)
        width = Inches(2.6)
        prs.slides[slide].shapes.add_picture('ppt-content/copywrite_2019.png', left, top, height=height, width=width)

        left = Inches(4.76)
        top = Inches(7.25)
        height = Inches(.24)
        width = Inches(.48)
        prs.slides[slide].shapes.add_picture('ppt-content/3M_logo.png', left, top, height=height, width=width)

    return prs 



def template_header(prs, title: str, slides_to_skip: list=[]):
    """ Inserts Inventor Recognition title header to slides """

    for slide in range(len(prs.slides)):
        if slide not in slides_to_skip:
            left = Inches(0.42)
            top = Inches(0.13)
            width = height = Inches(0.6)
            txtbox = prs.slides[slide].shapes.add_textbox(left, top, width, height)
            text_frame = txtbox.text_frame 

            p = text_frame.paragraphs[0]
            p.text = title 
            p.font.bold = False 
            p.font.size = Pt(30)
            p.font.name = 'Times New Roman'

    return prs 


def subtitle_header(slide, title: str):
    """ Creates subtitle under main slide title """
    top = Inches(0.61)
    left = Inches(0.42)
    width = height = Inches(0.5)
    txtbox = slide.shapes.add_textbox(left, top, width, height)
    text_frame = txtbox.text_frame 

    p = text_frame.paragraphs[0]
    p.text = title 
    p.font.bold = False 
    p.font.size = Pt(22)
    p.font.name = 'Times New Roman'

    return slide


def names_textbox(slide, box_num: int, names: list):
    """ Take a list of names and format them into a fixed box """
    top = Inches(0.68)
    width = Inches(3)
    height = Inches(7)
    if box_num == 0:
        # left-most textbox
        left = Inches(0.42)
    elif box_num == 1:
        # middle textbox
        left = Inches(3.3)
    elif box_num == 2:
        # right-most textbox
        left = Inches(6.3)
    else:
        print("WARNING: names_textbox only adds 3 boxes (box_num == 0:2)")
        return slide
    
    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    for name in names:
        p = tf.add_paragraph()
        p = tf.add_paragraph()
        p.text = name 
        p.font.bold = False
        p.font.name = '3M Circular TT Book'
        p.font.size = Pt(16)

    return slide 



def slide_creator(year: str, analysis: dict):
    """ High-level function for converting inventors spreadsheet to slides """

    print("Starting presentation creation.")
    prs = title_presentation(year)

    #prs = template_3M(prs)
    #prs = template_header(prs, f'Recognized Inventors of {year}', slides_to_skip=[0])

    if not os.path.exists('output/'):
        os.mkdir('output/')
        
    prs.save(f'output/Financial_Analysis_{year}.pptx')
