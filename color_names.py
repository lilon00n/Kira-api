# -*- coding: utf-8 -*-
"""
color_names.py
Places each color name as a text label at a position on the PDF page.
place: T=Top, B=Bottom, L=Left, R=Right
sideX: i=inward (text grows toward center), f=forward
sideY: i=inward, f=forward
Returns JSON {"retX": x, "retY": y} with the position after placing all names.
Migrated from PDFlib to reportlab + pypdf.
"""

import json
import os
from reportlab.pdfbase import pdfmetrics
from color_utils import make_spot_colors
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage

FONT_NAME = 'Helvetica'


def make(searchpath, pdffile, outfile, colors, fsize, x, y, place, sideX, sideY):
    fsize = float(fsize)
    x = float(x)
    y = float(y)

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)

    if place == 'L':
        angle = 90
    elif place == 'R':
        angle = 270
    else:
        angle = 0

    ret_x = -1
    ret_y = -1

    # Pre-measure all names (same for every page)
    # ReportLab stringWidth measures regardless of rotation
    dummy_widths = [pdfmetrics.stringWidth(c['name'], FONT_NAME, fsize)
                    for c in colors]
    text_height = fsize * 1.2  # approximate cap-height

    # Compute total width/height for initial offset calculation (mimics PDFlib info_textline on joined string)
    all_names = ''.join(c['name'] for c in colors)
    total_w = pdfmetrics.stringWidth(all_names, FONT_NAME, fsize)
    total_h = text_height  # single line height

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)
        c.setFont(FONT_NAME, fsize)

        cur_x = x
        cur_y = page_height - y  # flip to bottom-up

        # Apply initial offset based on sideX/sideY (mirrors PDFlib logic)
        if sideX == 'i':
            if place in ('T', 'B'):
                cur_x = cur_x - total_w
            elif place == 'R':
                cur_x = cur_x - total_h
            ret_x = cur_x
        else:
            if place == 'L':
                cur_x = cur_x + total_h

        if sideY == 'i':
            if place == 'B':
                cur_y = cur_y + total_h
            ret_y = cur_y
        else:
            if place == 'T':
                cur_y = cur_y - total_h

        for index, color in enumerate(colors):
            spot = spot_colors[color['name']]
            c.setFillColor(spot)
            text = color['name']
            tw = pdfmetrics.stringWidth(text, FONT_NAME, fsize)
            th = text_height

            # Determine draw position and text direction
            c.saveState()
            if place == 'L':
                if sideY == 'i':
                    c.translate(cur_x, cur_y)
                    c.rotate(angle)
                    c.drawString(0, 0, text)
                    cur_y = cur_y + tw
                else:
                    c.translate(cur_x, cur_y - tw)
                    c.rotate(angle)
                    c.drawString(0, 0, text)
                    cur_y = cur_y - tw
            elif place == 'R':
                if sideY == 'i':
                    c.translate(cur_x, cur_y + tw)
                    c.rotate(angle)
                    c.drawString(0, 0, text)
                    cur_y = cur_y + tw
                else:
                    c.translate(cur_x, cur_y)
                    c.rotate(angle)
                    c.drawString(0, 0, text)
                    cur_y = cur_y - tw
            elif place == 'T':
                if sideX == 'i':
                    c.drawString(cur_x - tw, cur_y, text)
                    cur_x = cur_x - tw
                else:
                    c.drawString(cur_x, cur_y, text)
                    cur_x = cur_x + tw
            else:  # B
                if sideX == 'i':
                    c.drawString(cur_x - tw, cur_y - th, text)
                    cur_x = cur_x - tw
                else:
                    c.drawString(cur_x, cur_y - th, text)
                    cur_x = cur_x + tw
            c.restoreState()

        if sideX == 'f':
            ret_x = cur_x
        if sideY == 'f':
            ret_y = cur_y

        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
    return json.dumps({'retX': ret_x, 'retY': page_height - ret_y})
