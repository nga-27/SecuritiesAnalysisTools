from pptx import Presentation
from pptx.util import Inches, Pt
import pandas as pd 
import numpy as np 
from datetime import datetime
import os 
import glob 

from libs.utils import fund_list_extractor, windows_compatible_file_parse

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


def make_MCI_slides(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])
    slide = fund_title_header(slide, 'Market Composite Index')
    
    content = f'output/temp/MCI.png'
    if os.path.exists(content):
        left = Inches(1.5)
        top = Inches(1.27)
        height = Inches(5.6)
        width = Inches(7.0)
        slide.shapes.add_picture(content, left, top, height=height, width=width)

    return prs


def make_fund_slides(prs, analysis: dict):
    funds = analysis.keys()
    for fund in funds:
        prs = add_fund_content(prs, fund)

    return prs


def add_fund_content(prs, fund: str):
    slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])
    indexes = []
    indexes.append(len(prs.slides) - 1)

    slide = fund_title_header(slide, fund)
    slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])
    slide = fund_title_header(slide, fund)
    indexes.append(len(prs.slides)-1)

    content_dir = f'output/temp/{fund}/'
    if os.path.exists(content_dir):
        content = content_dir + '*.png'
        pics = glob.glob(content)
        prs = format_plots(prs, indexes, pics)

    return prs


def fund_title_header(slide, fund: str):
    left = Inches(0) #Inches(3.86)
    top = Inches(0)
    width = height = Inches(0.5)
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

    return slide


def format_plots(prs, slide_indices: list, globs: list):
    parts = windows_compatible_file_parse(globs[0])

    header = parts[0] + '/' + parts[1] + '/' + parts[2] + '/'

    for globber in globs:

        globbed = windows_compatible_file_parse(globber)
        part = globbed[3]

        if 'cluster' in part:
            left = Inches(0)
            top = Inches(1.1)
            height = Inches(3.0)
            width = Inches(4.5)
            prs.slides[slide_indices[0]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'macd_bar' in part:
            left = Inches(4.5)
            top = Inches(1.1)
            height = Inches(3.0)
            width = Inches(4.5)
            prs.slides[slide_indices[0]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'moving_averages' in part:
            left = Inches(0.0)
            top = Inches(4.1)
            height = Inches(3.0)
            width = Inches(4.5)
            prs.slides[slide_indices[0]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'obv' in part:
            left = Inches(4.5)
            top = Inches(4.1)
            height = Inches(3.0)
            width = Inches(4.5)
            prs.slides[slide_indices[0]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'relative_strength' in part:
            left = Inches(0)
            top = Inches(1.1)
            height = Inches(3.0)
            width = Inches(4.5)
            prs.slides[slide_indices[1]].shapes.add_picture(header+part, left, top, height=height, width=width)

    return prs 



def slide_creator(year: str, analysis: dict):
    """ High-level function for converting inventors spreadsheet to slides """

    print("Starting presentation creation.")

    prs = title_presentation(year)
    prs = make_MCI_slides(prs)
    prs = make_fund_slides(prs, analysis)

    if not os.path.exists('output/'):
        os.mkdir('output/')
        
    prs.save(f'output/Financial_Analysis_{year}.pptx')
    print("Presentation created.")
