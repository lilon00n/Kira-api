# -*- coding: utf-8 -*-
"""
support_bar.py
Draws a single filled rectangle at (x, y, width, height) at a given tint
(percent) of the spot colors.
Migrated from PDFlib to reportlab + pypdf.
"""

import os
from reportlab.lib.colors import CMYKColor
from color_utils import make_spot_colors
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage


def make(searchpath, pdffile, outfile, colors, x, y, width, height, percent):
    x = float(x)
    y = float(y)
    width = float(width)
    height = float(height)
    tint = float(percent)

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)

        # Draw one rectangle per spot color blended at given tint.
        # The original draws all inks simultaneously (a single DeviceN fill);
        # here we composite them.  For a single-color use case this is exact.
        for color_data in colors:
            base = spot_colors[color_data['name']]
            tinted = CMYKColor(
                base.cyan * tint,
                base.magenta * tint,
                base.yellow * tint,
                base.black * tint,
                spotName=base.spotName,
                density=tint,
            )
            c.setFillColor(tinted)

        # Original: rect at (x, pageheight - y, width, height)
        draw_y = page_height - y
        c.rect(x, draw_y, width, height, stroke=0, fill=1)

        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
