import datetime
import numpy as np

import fpdf  # pylint: disable=F0401
from fpdf import FPDF  # pylint: disable=F0401

from libs.utils import INDEXES

from .pdf_utils import pdf_set_color_text, horizontal_spacer
from .pdf_utils import PDF_CONSTS


def fund_pdf_pages(pdf, analysis: dict, **kwargs):
    """Fund PDF Pages

    Arguments:
        pdf {FPDF} -- pdf object
        analysis {dict} -- data run data set

    Optional Args:
        views {str} -- (default: {None})

    Returns:
        FPDF -- pdf object
    """
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
            name = INDEXES.get(fund, fund)
            fund_data = analysis[fund]

            pdf.add_page()
            pdf = fund_title(pdf, name)
            pdf = fund_statistics(pdf, fund_data, sample_view=views)
            # pdf = fund_volatility(pdf, fund_data)
            pdf = beta_rsq(pdf, fund_data)

            for period in fund_data['synopsis']:
                pdf = metrics_tables(pdf, fund_data, period)
                pdf = latest_signals(pdf, fund_data, period)

    return pdf


def fund_title(pdf, name: str):
    """Fund Title

    Arguments:
        pdf {FPDF} -- pdf object
        name {str} -- name of fund to add

    Returns:
        FPDF -- pdf object
    """
    SPAN = pdf.w - 2 * pdf.l_margin
    pdf.set_font("Arial", size=36, style='B')
    pdf.cell(SPAN, 0.5, txt='', ln=1)
    pdf = pdf_set_color_text(pdf, "black")
    pdf.cell(SPAN, 1, txt=name, ln=1, align='C')
    return pdf


def metrics_tables(pdf, fund_data: dict, views: str, **kwargs):
    """Metrics Tables

    Arguments:
        pdf {FPDF} -- pdf object
        fund_data {dict} -- dataset of fund
        views {str} -- view/period of data

    Optional Args:
        num_metrics {int} -- number of metrics pair columns (default: {2})

    Returns:
        FPDF -- pdf object
    """
    num_metrics = kwargs.get('num_metrics', 2)

    pdf.ln(0.2)

    SPAN = pdf.w - 2 * pdf.l_margin
    col_width = SPAN / (2 * num_metrics)
    key_width = col_width + 0.5
    val_width = col_width - 0.5

    synopsis = fund_data['synopsis'][views]

    osc_keys = [osc for osc in synopsis['metrics_categories']['oscillator']]
    osc_values = []
    osc_deltas = []
    for osc in osc_keys:
        if synopsis['metrics'].get(osc) is not None:
            osc_values.append(np.round(synopsis['metrics'][osc], 5))
            osc_deltas.append(np.round(synopsis['metrics_delta'][osc], 5))
        else:
            osc_values.append('')
            osc_deltas.append('')

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

        if not isinstance(osc_values[i], (str)):
            if osc_values[i] < 0.0:
                colo[1] = "red"
            elif osc_values[i] > 0.0:
                colo[1] = "green"

        data.append(val)
        colors.append(colo)

    pdf = horizontal_spacer(pdf, 0.3)
    pdf = pdf_set_color_text(pdf, "black")
    pdf.set_font('Arial', style='B', size=14.0)
    pdf.cell(SPAN, 0.0, f'Metrics Data ({views})', align='C')

    FONT_SIZE = 8.0

    pdf.set_font('Arial', style='', size=FONT_SIZE)
    pdf.ln(0.5)
    height = pdf.font_size

    for j, row in enumerate(data):
        for i, col in enumerate(row):
            if i % 2 == 0:
                pdf = pdf_set_color_text(pdf, "black")
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

                pdf = pdf_set_color_text(pdf, colors[j][ind])
                pdf.set_font('Arial', style='', size=FONT_SIZE)
                pdf.cell(val_width, height, col_str,
                         align='L', border=0)

        pdf.ln(height * 2.0)

    return pdf


def fund_statistics(pdf, fund_data: dict, **kwargs):
    """Fund Statistics (from statistics)

    Arguments:
        pdf {FPDF} -- pdf object
        fund_data {dict} -- fund dataset

    Optional Args:
        sample_view {str} -- period of a fund (default: {None})

    Returns:
        FPDF -- pdf object
    """
    sample_view = kwargs.get('sample_view')
    if sample_view is None:
        for period in fund_data:
            if period != 'synopsis' and period != 'metadata':
                sample_view = period
                break

    SPAN = pdf.w - 2 * pdf.l_margin

    price = np.round(fund_data[sample_view]['statistics']['current_price'], 2)
    change = np.round(fund_data[sample_view]
                      ['statistics']['current_change'], 2)
    percent = np.round(fund_data[sample_view]
                       ['statistics']['current_percent_change'], 2)
    if change > 0.0:
        price_str = f"${price}   (+{change}, +{percent}%)"
    else:
        price_str = f"${price}   ({change}, {percent}%)"

    colo = "black"
    if change > 0.0:
        colo = "green"
    elif change < 0.0:
        colo = "red"

    pdf = pdf_set_color_text(pdf, colo)
    pdf.set_font('Arial', style='B', size=18.0)
    pdf.cell(SPAN, 0.3, txt=price_str, align='C', ln=1)

    pdf.ln(0.2)

    return pdf


def beta_rsq(pdf, fund_data: dict):
    """Beta R-Squared

    Arguments:
        pdf {FPDF} -- pdf object
        fund_data {dict} -- fund dataset

    Returns:
        FPDF -- pdf object
    """
    SPAN = pdf.w - 2 * pdf.l_margin

    left_keys = []
    right_keys = []
    left_vals = []
    right_vals = []

    for period in fund_data:
        if period != 'synopsis' and period != 'metadata':
            left_keys.append(f"Beta ({period})")
            right_keys.append(f"R-squared ({period})")
            left_keys.append(f"Alpha ({period})")
            right_keys.append(f"Sharpe Ratio ({period})")

            if fund_data[period]['statistics'].get('risk_ratios') is None:
                left_vals.append('')
                right_vals.append('')
                left_vals.append('')
                right_vals.append('')

            else:
                risk_factors = fund_data[period]['statistics']['risk_ratios']
                left_vals.append(
                    str(np.round(risk_factors['beta']['market'], 5)))
                right_vals.append(
                    str(np.round(risk_factors['r_squared']['market'], 5)))
                left_vals.append(
                    str(np.round(risk_factors['alpha']['market'], 5)))
                if isinstance(risk_factors['sharpe'], (float, int)):
                    right_vals.append(
                        str(np.round(risk_factors['sharpe'], 5)))
                else:
                    right_vals.append(risk_factors['sharpe'])

    data = []
    for i in range(len(left_keys)):
        printable = [left_keys[i], left_vals[i], right_keys[i], right_vals[i]]
        data.append(printable)

    pdf = pdf_set_color_text(pdf, "black")
    pdf.set_font('Arial', style='B', size=10.0)
    pdf = horizontal_spacer(pdf, 0.3)
    height = pdf.font_size

    quad = SPAN / 4.0
    quad_name = quad + 0.5
    quad_val = quad - 0.5

    for row in data:
        for i, col in enumerate(row):
            if i % 2 == 0:
                pdf.cell(quad_name, height, str(col), align='L', border=0)
            else:
                pdf.cell(quad_val, height, str(col), align='L', border=0)
        pdf.ln(height * 1.3)
    return pdf


def fund_volatility(pdf, fund_data: dict):
    """Fund Volatility

    If Volatility Quotient is present

    Arguments:
        pdf {FPDF} -- pdf object
        fund_data {dict} -- fund dataset

    Returns:
        FPDF -- pdf object
    """
    SPAN = pdf.w - 2 * pdf.l_margin

    vq = fund_data['metadata'].get('volatility', {})
    status = vq.get('status', {}).get('status', '')
    color = vq.get('status', {}).get('color', "black")
    vol_str = f"Stop Loss Status: {status}"

    pdf = pdf_set_color_text(pdf, color)
    pdf.set_font('Arial', style='B', size=16.0)
    pdf.cell(SPAN, 0.4, txt=vol_str, align='C', ln=1)

    vol = vq.get("VQ", "")
    vq_str = f"Current Volatility:"
    vq_str2 = f"{vol}%"
    max_price = vq.get("last_max", {}).get("Price", "")
    mp_str = f"Last relative max price:"
    mp_str2 = f"${max_price}"

    pdf = horizontal_spacer(pdf, 0.2)

    quad = SPAN / 4.0
    quad_name = quad + 0.5
    quad_val = quad - 0.5

    pdf = pdf_set_color_text(pdf, "blue")
    pdf.set_font('Arial', style='B', size=12.0)
    pdf.cell(quad_name, 0.2, txt=vq_str, align='L')
    pdf.cell(quad_val, 0.2, txt=vq_str2, align='L')
    pdf.cell(quad_name, 0.2, txt=mp_str, align='L')
    pdf.cell(quad_val, 0.2, txt=mp_str2, align='L', ln=1)

    stop_loss = vq.get("stop_loss", "")
    sl_str = f"Current Stop Loss:"
    sl_str2 = f"${stop_loss}"
    max_date = vq.get("last_max", {}).get("Date", "")
    md_str = f"Date of last relative max:"
    md_str2 = f"{max_date}"

    pdf.cell(quad_name, 0.2, txt=sl_str, align='L')
    pdf.cell(quad_val, 0.2, txt=sl_str2, align='L')
    pdf.cell(quad_name, 0.2, txt=md_str, align='L')
    pdf.cell(quad_val, 0.2, txt=md_str2, align='L', ln=1)

    altman_z = fund_data['metadata'].get('altman_z', {})
    altman_z_score = altman_z.get('score')

    if isinstance(altman_z_score, (int, float)):
        altman_z_score = str(np.round(altman_z_score, 5))

    az_str = f"Altman-Z Score:"
    az_str2 = altman_z_score

    pdf.cell(quad_name, 0.2, txt=az_str, align='L')
    pdf.cell(quad_val, 0.2, txt=az_str2, align='L')

    return pdf


def latest_signals(pdf, fund_data: dict, views: str, **kwargs):
    """Latest Signals

    Arguments:
        pdf {pdf-object} -- pdf to create
        fund_data {dict} -- fund data
        views {str} -- period to create

    Returns:
        pdf-object -- pdf modified
    """
    signals = fund_data[views].get('last_signals')
    if signals is None:
        return pdf

    signals = signals["signals"]

    SPAN = pdf.w - 2 * pdf.l_margin
    col_width = SPAN / 4
    key_width = col_width - 0.5
    val_width = col_width + 0.5

    pdf.ln(0.5)

    pdf = pdf_set_color_text(pdf, "black")
    pdf.set_font('Arial', style='B', size=14.0)
    pdf.cell(SPAN, 0.0, f'Latest Signals ({views})', align='C')

    data = [["Time Period", "Date", "Indicator", "Signal Found"]]
    colors = ["black"]

    for sig in signals:
        row = []
        row.append(f"({sig['days_ago']}) days ago")
        row.append(f"{sig['date']}")
        row.append(f"{sig['indicator']}")
        row.append(f"{sig['value']}")

        data.append(row)

        if sig['type'] == 'bearish':
            colors.append('red')
        else:
            colors.append('green')

    FONT_SIZE = 8.0
    pdf.set_font('Arial', style='', size=FONT_SIZE)
    pdf.ln(0.4)
    height = pdf.font_size

    for j, row in enumerate(data):
        for i, col in enumerate(row):
            if i == 0 or i == 1:
                pdf = pdf_set_color_text(pdf, colors[j])
                pdf.set_font('Arial', style='B', size=FONT_SIZE)
                pdf.cell(key_width, height, str(col),
                         align='L', border=0)

            else:
                col_str = col
                pdf = pdf_set_color_text(pdf, colors[j])
                pdf.set_font('Arial', style='B', size=FONT_SIZE)
                pdf.cell(val_width, height, col_str,
                         align='L', border=0)

        pdf.ln(height * 2.0)

    return pdf
