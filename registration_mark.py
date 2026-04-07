# -*- coding: utf-8 -*-
"""
registration_mark.py
Draws a registration mark (cross + concentric circles) at a given position
on every page of a PDF.
Migrated from PDFlib to reportlab + pypdf.
"""

import os
import math
from reportlab.lib.colors import white as rl_white
from color_utils import make_spot_colors, get_all_inks_color
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage


def _draw_reg_mark(c, cx, cy, radius, mark_color, lw):
    """
    Render a standard prepress registration mark centred at (cx, cy).
    Structure:
      - Cross lines spanning the full diameter
      - Filled inner circle (radius/3)
      - White lines on inner radius
      - Outer stroke circle (2*radius/3)
    """
    c.setLineWidth(lw)

    # Cross lines
    c.setStrokeColor(mark_color)
    c.line(cx - radius, cy, cx + radius, cy)
    c.line(cx, cy - radius, cx, cy + radius)

    # Filled inner circle
    c.setFillColor(mark_color)
    c.circle(cx, cy, radius / 3, stroke=0, fill=1)

    # White inner cross (hides centre of cross lines to create the classic look)
    c.setStrokeColor(rl_white)
    c.setLineWidth(lw)
    c.line(cx - radius / 3, cy, cx + radius / 3, cy)
    c.line(cx, cy - radius / 3, cx, cy + radius / 3)

    # Outer ring
    c.setStrokeColor(mark_color)
    c.circle(cx, cy, 2 * radius / 3, stroke=1, fill=0)


def make(searchpath, pdffile, outfile, colors, x, y, crop_size, weight):
    x = float(x)
    y = float(y)
    crop_size = float(crop_size)
    lw = float(weight)

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)
    mark_color = get_all_inks_color(spot_colors)

    # y is measured from the top in original PDFlib code
    cy = page_height - y

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)
        _draw_reg_mark(c, x, cy, crop_size, mark_color, lw)
        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
