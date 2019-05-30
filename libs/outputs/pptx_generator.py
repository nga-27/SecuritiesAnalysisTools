from pptx import Presentation
from pptx.util import Inches, Pt
import pandas as pd 
import numpy as np 
from datetime import datetime
import os 
import glob 

from libs.utils import fund_list_extractor

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


def make_fund_slides(prs, analysis: dict):
    funds = analysis.keys()
    for fund in funds:
        prs = add_fund_content(prs, fund)

    return prs


def add_fund_content(prs, fund: str):
    left = Inches(0) #Inches(3.86)
    top = Inches(0)
    width = height = Inches(0.5)

    slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])

    txbox = slide.shapes.add_textbox(left, top, width, height)
    tf = txbox.text_frame
    #p = tf.add_paragraph()
    p = tf.paragraphs[0]
    p.text = fund 
    p.font.size = Pt(36)
    p.font.name = 'Arial'
    p.font.bold = True

    p = tf.add_paragraph()
    p.font.size = Pt(16)
    p.font.bold = False
    p.text = str(datetime.now())

    content_dir = f'output/temp/{fund}/'
    if os.path.exists(content_dir):
        content = content_dir + '*.png'
        pics = glob.glob(content)
        slide = format_plots(slide, pics)

    return prs


def format_plots(slide, globs: list):
    print(globs)
    parts = globs[0].split('/')
    header = parts[0] + '/' + parts[1] + '/' + parts[2] + '/'

    for globber in globs:
        part = globber.split('/')[3]

        if 'clustered' in part:
            left = Inches(0)
            top = Inches(2.0)
            height = Inches(2.0)
            width = Inches(3.0)
            #slide.shapes.
    return slide 


def slide_creator(year: str, analysis: dict):
    """ High-level function for converting inventors spreadsheet to slides """

    print("Starting presentation creation.")
    prs = title_presentation(year)

    prs = make_fund_slides(prs, analysis)

    #prs = template_3M(prs)
    #prs = template_header(prs, f'Recognized Inventors of {year}', slides_to_skip=[0])

    if not os.path.exists('output/'):
        os.mkdir('output/')
        
    prs.save(f'output/Financial_Analysis_{year}.pptx')
