PDF_CONSTS = {
    "span": 8.5
}


def pdf_set_color_text(pdf, color: str):
    color = color_to_RGB_array(color)
    pdf.set_text_color(color[0], color[1], color[2])
    return pdf


def color_to_RGB_array(color: str):
    if color == 'black':
        return [0x00, 0x00, 0x00]
    elif color == 'blue':
        return [0x00, 0x00, 0xFF]
    elif color == 'green':
        return [0x00, 0xCC, 0x00]
    elif color == 'purple':
        return [0x7F, 0x00, 0xFF]
    elif color == 'yellow':
        return [0xee, 0xd4, 0x00]
    elif color == 'orange':
        return [0xff, 0x99, 0x33]
    elif color == 'red':
        return [0xff, 0x00, 0x00]
    else:
        print(f"WARNING: Color '{color}' not found in 'color_to_RGB_array'")
        return [0x00, 0x00, 0x00]


def horizontal_spacer(pdf, height: float):
    pdf.ln(height)
    return pdf
