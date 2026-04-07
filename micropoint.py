# -*- coding: utf-8 -*-
"""
micropoint.py
Draws a micropoint: a white outer circle + a spot-colored inner circle.
Used as a fine registration aid on prepress sheets.
Migrated from PDFlib to reportlab + pypdf.
"""

import os
from reportlab.lib.colors import white as rl_white
from color_utils import make_spot_colors, get_all_inks_color
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage

# PDFlib used radius / 0.3514729 as the Bezier control factor for circles.
# In ReportLab we call circle() directly so no conversion needed.
# The original radius param is used as-is.


def _draw_micropoint(c, cx, cy, radius, mark_color):
    """
    White outer disc + spot-colored inner disc.
    Radius of outer disc = radius / 0.3514729 in original (Bezier approx).
    We use the same scaling factor for visual parity.
    """
    outer_r = radius / 0.3514729
    inner_r = (radius / 2) / 0.3514729

    # Outer white circle
    c.setFillColor(rl_white)
    c.setLineWidth(0.01)
    c.circle(cx, cy, outer_r, stroke=0, fill=1)

    # Inner spot-colored circle
    c.setFillColor(mark_color)
    c.circle(cx, cy, inner_r, stroke=0, fill=1)


def make(searchpath, pdffile, outfile, colors, x, y, crop_size):
    x = float(x)
    y = float(y)
    crop_size = float(crop_size)

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)
    mark_color = get_all_inks_color(spot_colors)

    cy = page_height - y

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)
        _draw_micropoint(c, x, cy, crop_size, mark_color)
        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
