from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

import pandas as pd 
import numpy as np 
import os 
import glob 

from libs.utils import fund_list_extractor, windows_compatible_file_parse
from .slide_utils import slide_title_header, color_to_RGB

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


def make_fund_slides(prs, analysis: dict):
    funds = analysis.keys()
    for fund in funds:
        prs = add_fund_content(prs, fund, analysis)

    return prs


def add_fund_content(prs, fund: str, analysis: dict):
    content_dir = f'output/temp/{fund}/'
    if os.path.exists(content_dir):
        # Title slide for a fund
        slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])
        top = Inches(0.1)
        left = Inches(4)
        width = Inches(5)
        height = Inches(2)
        txtbox = slide.shapes.add_textbox(left, top, width, height)
        text_frame = txtbox.text_frame

        p = text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = f'{fund}'
        p.font.bold = True
        p.font.size = Pt(60)
        p.font.name = 'Arial'

        p2 = text_frame.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.text = f"Dates Covered: {analysis[fund]['dates_covered']['start']}  :  {analysis[fund]['dates_covered']['end']}"
        p2.font.bold = False
        p2.font.size = Pt(18)
        p2.font.color.rgb = RGBColor(0x74, 0x3c, 0xe6)
        p2.font.name = 'Arial'

        has_beta = False
        if 'beta' in analysis[fund].keys():
            # Insert a table of fund figures
            left_loc = Inches(0.1)
            top_loc = Inches(1.1)
            table_width = Inches(2.4)
            table_height = Inches(1.4)

            table_placeholder = slide.shapes.add_table( 3, 
                                                        2,
                                                        left_loc,
                                                        top_loc,
                                                        table_width,
                                                        table_height)
            table = table_placeholder.table

            table.cell(0,0).text = 'Attribute'
            table.cell(0,1).text = ''
            table.cell(1,0).text = 'Beta'
            table.cell(1,1).text = str(np.round(analysis[fund]['beta'], 5))
            table.cell(2,0).text = 'R-Squared'
            table.cell(2,1).text = str(np.round(analysis[fund]['r_squared'], 5))

            table.cell(0, 0).text_frame.paragraphs[0].font.size = Pt(16)
            table.cell(0, 1).text_frame.paragraphs[0].font.size = Pt(16)
            for i in range(1,3):
                table.cell(i, 0).text_frame.paragraphs[0].font.size = Pt(14)
                table.cell(i, 1).text_frame.paragraphs[0].font.size = Pt(14)
            has_beta = True

        content = content_dir + f"candlestick_{fund}.png"
        if os.path.exists(content):
            if has_beta:
                left = Inches(2.6) #Inches(1.42)
            else:
                left = Inches(1.42)
            top = Inches(1.4)
            height = Inches(6)
            width = Inches(10.5)
            slide.shapes.add_picture(content, left, top, height=height, width=width)

        # Slide #1 of content
        slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])
        indexes = []
        indexes.append(len(prs.slides) - 1)
        slide = slide_title_header(slide, fund)

        # Slide #2 of content
        slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])
        slide = slide_title_header(slide, fund)
        indexes.append(len(prs.slides)-1)

        # Slide #3 of content
        slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])
        slide = slide_title_header(slide, fund)
        indexes.append(len(prs.slides)-1)

        # Slide #4 of content
        slide = prs.slides.add_slide(prs.slide_layouts[BLANK_SLIDE])
        slide = slide_title_header(slide, fund)
        indexes.append(len(prs.slides)-1)

        content = content_dir + '*.png'
        pics = glob.glob(content)
        fund_analysis = analysis[fund]
        prs = format_plots(prs, indexes, pics, fund_analysis=fund_analysis)

    return prs


def format_plots(prs, slide_indices: list, globs: list, fund_analysis: dict={}):
    parts = windows_compatible_file_parse(globs[0])

    header = parts[0] + '/' + parts[1] + '/' + parts[2] + '/'

    for globber in globs:

        globbed = windows_compatible_file_parse(globber)
        part = globbed[3]

        if 'cluster' in part:
            left = Inches(0)
            top = Inches(1.1)
            height = Inches(3.0)
            width = Inches(6.5)
            prs.slides[slide_indices[0]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'macd_bar' in part:
            left = Inches(6.5)
            top = Inches(1.1)
            height = Inches(3.0)
            width = Inches(6.5)
            prs.slides[slide_indices[0]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'simple_moving_averages' in part:
            left = Inches(0.0)
            top = Inches(4.1)
            height = Inches(3.0)
            width = Inches(6.5)
            prs.slides[slide_indices[0]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'obv' in part:
            left = Inches(6.5)
            top = Inches(4.1)
            height = Inches(3.0)
            width = Inches(6.5)
            prs.slides[slide_indices[0]].shapes.add_picture(header+part, left, top, height=height, width=width)

        ### Slide #2

        if 'relative_strength' in part:
            left = Inches(0)
            top = Inches(1.1)
            height = Inches(3.0)
            width = Inches(6.5)
            prs.slides[slide_indices[1]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'exp_moving_averages' in part:
            left = Inches(6.5)
            top = Inches(1.1)
            height = Inches(3.0)
            width = Inches(6.5)
            prs.slides[slide_indices[1]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'swing_trades' in part:
            left = Inches(0.0)
            top = Inches(4.1)
            height = Inches(3.0)
            width = Inches(6.5)
            prs.slides[slide_indices[1]].shapes.add_picture(header+part, left, top, height=height, width=width)

        if 'head_and_shoulders' in part:
            left = Inches(6.5)
            top = Inches(4.1)
            height = Inches(3.0)
            width = Inches(6.5)
            prs.slides[slide_indices[1]].shapes.add_picture(header+part, left, top, height=height, width=width)

        # Slide #3

        if 'resist_support' in part:
            left = Inches(0)
            top = Inches(1.55)
            height = Inches(4.7)
            width = Inches(7)
            prs.slides[slide_indices[2]].shapes.add_picture(header+part, left, top, height=height, width=width)

            left = Inches(7)
            top = Inches(0.25)
            height = Inches(4.7)
            width = Inches(4)
            txbox = prs.slides[slide_indices[2]].shapes.add_textbox(left, top, width, height)
            
            tf = txbox.text_frame
            p = tf.paragraphs[0]
            p.text = f"Nearest Support & Resistance Levels"
            p.font.size = Pt(18)
            p.font.name = 'Arial'
            p.font.bold = True

            p = tf.add_paragraph()
            p.text = f"Current Price ${fund_analysis['support_resistance']['current price']}"
            p.font.size = Pt(16)
            p.font.name = 'Arial'
            p.font.bold = True

            left_loc = Inches(8)
            top_loc = Inches(1)
            table_width = Inches(4)

            num_srs = len(fund_analysis['support_resistance']['major S&R']) + 1
            table_height = Inches(num_srs * 0.33)
            if num_srs * 0.33 > 6.0:
                table_height = Inches(6.0)

            table_placeholder = prs.slides[slide_indices[2]].shapes.add_table(
                                                    num_srs, 
                                                    2,
                                                    left_loc,
                                                    top_loc,
                                                    table_width,
                                                    table_height)
            table = table_placeholder.table

            table.cell(0,0).text = 'Price'
            table.cell(0,1).text = '% Change'

            for i, maj in enumerate(fund_analysis['support_resistance']['major S&R']):
                table.cell(i+1, 0).text = f"${maj['Price']}"
                table.cell(i+1, 1).text = f"{maj['Change']}"
                fl = maj['Change'].split('%')[0]
                # if float(fl) >= 0.0:
                #     table.cell(i+1, 0).text_frame.paragraphs[0].font.color.rgb = RGBColor(0xeb, 0x0e, 0x1d)
                #     table.cell(i+1, 1).text_frame.paragraphs[0].font.color.rgb = RGBColor(0xeb, 0x0e, 0x1d)
                # else:
                #     table.cell(i+1, 0).text_frame.paragraphs[0].font.color.rgb = RGBColor(0x33, 0xb3, 0x2e)
                #     table.cell(i+1, 1).text_frame.paragraphs[0].font.color.rgb = RGBColor(0x33, 0xb3, 0x2e)
                color = color_to_RGB(maj['Color'])
                table.cell(i+1, 0).text_frame.paragraphs[0].font.color.rgb = color
                table.cell(i+1, 1).text_frame.paragraphs[0].font.color.rgb = color

        # Slide 4
        if 'trendline' in part:
            left = Inches(0)
            top = Inches(1.55)
            height = Inches(4.7)
            width = Inches(7)
            prs.slides[slide_indices[3]].shapes.add_picture(header+part, left, top, height=height, width=width)

            left = Inches(7)
            top = Inches(0.25)
            height = Inches(4.7)
            width = Inches(4)
            txbox = prs.slides[slide_indices[3]].shapes.add_textbox(left, top, width, height)
            
            tf = txbox.text_frame
            p = tf.paragraphs[0]
            p.text = f"Long, Intermediate, Short, and Near Term Trends"
            p.font.size = Pt(18)
            p.font.name = 'Arial'
            p.font.bold = True

            p = tf.add_paragraph()
            # TODO: need to inplement trendline analysis here
            p.text = f"Current Price ${fund_analysis['support_resistance']['current price']}"
            p.font.size = Pt(16)
            p.font.name = 'Arial'
            p.font.bold = True

            for trend in fund_analysis['trendlines']:
                if trend['current']:
                    print(f"current trend: {trend['type']}, {trend['start']}, {trend['end']}")

    return prs 