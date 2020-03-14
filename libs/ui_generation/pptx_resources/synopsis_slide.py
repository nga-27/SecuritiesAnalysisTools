import os
import numpy as np

from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

from .slide_utils import pptx_ui_errors, color_to_RGB


def generate_synopsis_slide(slide, analysis: dict, fund: str, **kwargs):

    views = kwargs.get('views')
    if views is None:
        return pptx_ui_errors(slide, "No 'views' object passed.")

    synopsis = analysis[fund]['synopsis'][views]
    slide = add_synopsis_title(slide, f"Metrics Summary ({views})")

    slide = add_synopsis_category_box(
        slide, 'trend', synopsis, type_='metrics')
    slide = add_synopsis_category_box(
        slide, 'oscillator', synopsis, type_='metrics')

    return slide


def add_synopsis_title(slide, title: str):

    top = Inches(0.7)
    left = Inches(4)
    width = Inches(5)
    height = Inches(2)
    txtbox = slide.shapes.add_textbox(left, top, width, height)
    text_frame = txtbox.text_frame

    p = text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = f'{title}'
    p.font.bold = True
    p.font.size = Pt(40)
    p.font.name = 'Arial'
    return slide


def add_synopsis_category_box(slide, category: str, content: dict, type_='metrics'):

    cat = type_ + "_categories"
    listed = content.get(cat, {}).get(category, [])

    if type_ == 'metrics':

        if category == 'trend':

            # Trend Metrics Table
            top = Inches(1.5)
            left = Inches(0.25)
            width = Inches(4.65)
            height = Inches(.58)
            txtbox = slide.shapes.add_textbox(left, top, width, height)
            text_frame = txtbox.text_frame

            p = text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.text = f'Trend-Based Metrics'
            p.font.bold = True
            p.font.size = Pt(20)
            p.font.name = 'Arial'

            table_height = Inches(4)
            table_width = Inches(4.65)
            left_loc = left
            top_loc = Inches(2.08)
            table_placeholder = slide.shapes.add_table(len(listed) + 1,
                                                       2,
                                                       left_loc,
                                                       top_loc,
                                                       table_width,
                                                       table_height)
            table = table_placeholder.table

            table.cell(0, 0).text = "Current vs. Metric"
            table.cell(0, 1).text = "Current (Previous)"

            for i, item in enumerate(listed):
                item_str = pretty_up_key(item)
                value = content.get('metrics', {}).get(item, 0.0)
                delta = content.get('metrics_delta', {}).get(item, 0.0)

                value_str = f"{value}%\t"
                delta_str = f"({delta}%)"
                if value > 0.0:
                    value_str = f"+{value}%\t"
                if delta > 0.0:
                    delta_str = f"(+{delta}%)"
                value_str = value_str + delta_str

                table.cell(i+1, 0).text = item_str
                table.cell(i+1, 1).text = value_str
                table.cell(i+1, 0).text_frame.paragraphs[0].font.size = Pt(12)
                table.cell(i+1, 1).text_frame.paragraphs[0].font.size = Pt(14)

                if value > 0.0:
                    table.cell(i+1, 1).text_frame.paragraphs[0].font.color.rgb = \
                        color_to_RGB("green")
                elif value < 0.0:
                    table.cell(i+1, 1).text_frame.paragraphs[0].font.color.rgb = \
                        color_to_RGB("red")

            # A note about moving averages
            note = "'Current vs. Metric' refers to difference between moving average metric " + \
                "and current close. A negative % refers to a close X% less than the metric. " + \
                "(Previous) is the previous period's close percent difference. This is " + \
                "supplied to see change to current day."

            top = Inches(6.9)
            left = Inches(0.25)
            width = Inches(4.65)
            height = Inches(0.56)
            txtbox2 = slide.shapes.add_textbox(left, top, width, height)
            text_frame = txtbox2.text_frame
            text_frame.word_wrap = True

            p = text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT
            p.text = note
            p.font.bold = False
            p.font.size = Pt(8)
            p.font.name = 'Arial'

        elif category == 'oscillator':
            # Oscillator Metrics Table
            top = Inches(1.5)
            left = Inches(5.25)
            width = Inches(4.65)
            height = Inches(.58)
            txtbox = slide.shapes.add_textbox(left, top, width, height)
            text_frame = txtbox.text_frame

            p = text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.text = f'Oscillator-Based Metrics'
            p.font.bold = True
            p.font.size = Pt(20)
            p.font.name = 'Arial'

            table_height = Inches(4)
            table_width = Inches(4.65)
            left_loc = left
            top_loc = Inches(2.08)
            table_placeholder = slide.shapes.add_table(len(listed) + 1,
                                                       2,
                                                       left_loc,
                                                       top_loc,
                                                       table_width,
                                                       table_height)
            table = table_placeholder.table

            table.cell(0, 0).text = "Metric"
            table.cell(0, 1).text = "Current (Previous)"

            for i, item in enumerate(listed):
                item_str = pretty_up_key(item)
                value = content.get('metrics', {}).get(item, 0.0)
                delta = content.get('metrics_delta', {}).get(item, 0.0)

                value_str = f"{np.round(value, 5)}"
                if len(value_str) < 5:
                    value_str = f"{np.round(value, 5)}\t\t"
                else:
                    value_str = f"{np.round(value, 5)}\t"
                delta_str = f"({np.round(delta, 5)})"
                value_str = value_str + delta_str

                table.cell(i+1, 0).text = item_str
                table.cell(i+1, 1).text = value_str
                table.cell(i+1, 0).text_frame.paragraphs[0].font.size = Pt(12)
                table.cell(i+1, 1).text_frame.paragraphs[0].font.size = Pt(14)

                if value > 0.0:
                    table.cell(i+1, 1).text_frame.paragraphs[0].font.color.rgb = \
                        color_to_RGB("green")
                elif value < 0.0:
                    table.cell(i+1, 1).text_frame.paragraphs[0].font.color.rgb = \
                        color_to_RGB("red")

    return slide


def pretty_up_key(key: str) -> str:
    keys = key.split('_')
    keys = [new_key.capitalize() for new_key in keys]
    output = ' '.join(keys)
    return output
