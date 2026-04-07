# -*- coding: utf-8 -*-
"""
info.py
Places a text string at a position on the PDF page.
Same place / sideX / sideY coordinate system as color_names.py.
Returns JSON {"retX": x, "retY": y}.
Migrated from PDFlib to reportlab + pypdf.
"""

import json
import os
from reportlab.pdfbase import pdfmetrics
from color_utils import make_spot_colors, get_all_inks_color
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage

FONT_NAME = 'Helvetica'


def make(searchpath, pdffile, outfile, colors, info, fsize, x, y, place, sideX, sideY):
    fsize = float(fsize)
    x = float(x)
    y = float(y)

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)
    mark_color = get_all_inks_color(spot_colors)

    if place == 'L':
        angle = 90
    elif place == 'R':
        angle = 270
    else:
        angle = 0

    total_w = pdfmetrics.stringWidth(info, FONT_NAME, fsize)
    total_h = fsize * 1.2  # approximate line height

    ret_x = -1
    ret_y = -1

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)
        c.setFont(FONT_NAME, fsize)
        c.setFillColor(mark_color)

        cur_x = x
        cur_y = page_height - y

        # Offset logic mirrors PDFlib info_textline placement
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
            elif place in ('R', 'L'):
                cur_y = cur_y + total_w
            ret_y = cur_y
        else:
            if place == 'T':
                cur_y = cur_y - total_h

        c.saveState()
        if place == 'L':
            c.translate(cur_x, cur_y - total_w)
            c.rotate(angle)
            c.drawString(0, 0, info)
            if sideY != 'i':
                cur_y = cur_y - total_w
        elif place == 'R':
            c.translate(cur_x, cur_y)
            c.rotate(angle)
            c.drawString(0, 0, info)
            if sideY != 'i':
                cur_y = cur_y - total_w
        elif place == 'T':
            c.drawString(cur_x, cur_y, info)
            if sideX == 'i':
                cur_x = cur_x - total_w
            else:
                cur_x = cur_x + total_w
        else:  # B
            c.drawString(cur_x, cur_y - total_h, info)
            if sideX == 'i':
                cur_x = cur_x - total_w
            else:
                cur_x = cur_x + total_w
        c.restoreState()

        if sideX == 'f':
            ret_x = cur_x
        if sideY == 'f':
            ret_y = cur_y

        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
    return json.dumps({'retX': ret_x, 'retY': page_height - ret_y})
