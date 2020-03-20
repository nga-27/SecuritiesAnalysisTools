import datetime
import numpy as np

import fpdf  # pylint: disable=F0401
from fpdf import FPDF  # pylint: disable=F0401

from libs.utils import SP500

from .pdf_utils import color_to_RGB_array, horizontal_spacer
from .pdf_utils import PDF_CONSTS


def fund_pdf_pages(pdf, analysis: dict, **kwargs):

    views = kwargs.get('views')

    has_view = False
    if views is None:
        for fund in analysis:
            for period in analysis[fund]:
                views = period
                has_view = True
                break
            if has_view:
                break

    for fund in analysis:
        if fund != '_METRICS_':
            name = SP500.get(fund, fund)
            fund_data = analysis[fund]

            pdf.add_page()
            pdf = fund_title(pdf, name)

            for period in analysis[fund]['synopsis']:
                pdf = metrics_tables(pdf, fund_data, period)

    return pdf


def fund_title(pdf, name: str):

    SPAN = pdf.w - 2 * pdf.l_margin
    pdf.set_font("Arial", size=36, style='B')
    pdf.cell(SPAN, 0.5, txt='', ln=1)
    color = color_to_RGB_array('black')
    pdf.set_text_color(color[0], color[1], color[2])
    pdf.cell(SPAN, 1, txt=name, ln=1, align='C')
    return pdf


def metrics_tables(pdf, fund_data: dict, views: str, **kwargs):

    num_metrics = kwargs.get('num_metrics', 2)

    SPAN = pdf.w - 2 * pdf.l_margin
    col_width = SPAN / (2 * num_metrics)
    key_width = col_width + 0.5
    val_width = col_width - 0.5

    synopsis = fund_data['synopsis'][views]

    osc_keys = [osc for osc in synopsis['metrics_categories']['oscillator']]
    osc_values = [np.round(synopsis['metrics'][osc], 5) for osc in osc_keys]
    osc_deltas = [np.round(synopsis['metrics_delta'][osc], 5)
                  for osc in osc_keys]
    trend_keys = [
        f"{trend} %" for trend in synopsis['metrics_categories']['trend']]
    trend_values = [np.round(synopsis['metrics'][trend], 5)
                    for trend in synopsis['metrics_categories']['trend']]
    trend_deltas = [np.round(synopsis['metrics_delta'][trend], 5)
                    for trend in synopsis['metrics_categories']['trend']]

    # Assumption that metrics oscillators will be longer than trends
    for _ in range(len(osc_keys)-len(trend_keys)):
        trend_keys.append("")
        trend_values.append("")
        trend_deltas.append("")

    data = []
    colors = []
    for i in range(len(osc_keys)):
        val = [trend_keys[i], trend_values[i], osc_keys[i], osc_values[i]]
        colo = ["black", "black"]
        if not isinstance(trend_values[i], (str)):
            if trend_values[i] < 0.0:
                colo[0] = "red"
            elif trend_values[i] > 0.0:
                colo[0] = "green"

        if osc_values[i] < 0.0:
            colo[1] = "red"
        elif osc_values[i] > 0.0:
            colo[1] = "green"

        data.append(val)
        colors.append(colo)

    pdf = horizontal_spacer(pdf, 0.3)
    color = color_to_RGB_array("black")
    pdf.set_text_color(color[0], color[1], color[2])
    pdf.set_font('Arial', style='B', size=14.0)
    pdf.cell(SPAN, 0.0, f'Metrics Data ({views})', align='C')

    FONT_SIZE = 8.0

    pdf.set_font('Arial', style='', size=FONT_SIZE)
    pdf.ln(0.5)
    height = pdf.font_size

    for j, row in enumerate(data):
        for i, col in enumerate(row):
            if i % 2 == 0:
                color = color_to_RGB_array("black")
                pdf.set_text_color(color[0], color[1], color[2])
                pdf.set_font('Arial', style='B', size=FONT_SIZE)
                pdf.cell(key_width, height, str(col),
                         align='L', border=0)

            else:
                ind = int(i / 2)
                col_str = f"{col}"
                if (ind == 0) and (trend_deltas[j] != ''):
                    col_str = f"{col}  ({trend_deltas[j]})"
                if (ind == 1):
                    col_str = f"{col}  ({osc_deltas[j]})"
                color = color_to_RGB_array(colors[j][ind])
                pdf.set_text_color(color[0], color[1], color[2])
                pdf.set_font('Arial', style='', size=FONT_SIZE)
                pdf.cell(val_width, height, col_str,
                         align='L', border=0)

        pdf.ln(height * 2.0)

    return pdf
