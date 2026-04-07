# -*- coding: utf-8 -*-
"""
crop_mark.py
Adds L-shaped crop marks at all four corners of every page of a PDF.
Migrated from PDFlib to reportlab + pypdf.
"""

import os
from color_utils import make_spot_colors, get_all_inks_color
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage


def make(searchpath, pdffile, outfile, colors, x_margin, y_margin, size, width,
         height, dist_width, dist_height, weight):
    x_margin = float(x_margin)
    y_margin = float(y_margin)
    size = float(size)
    width = float(width)
    height = float(height)
    lw = float(weight)
    dist_width = float(dist_width)
    dist_height = float(dist_height)

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)
    mark_color = get_all_inks_color(spot_colors)

    # Original PDFlib code remapped y_margin from top: y_margin = pageheight - y_margin
    # So top_y is the base reference, bottom_y = top_y - height
    top_y = page_height - y_margin
    bottom_y = top_y - height
    left_x = x_margin
    right_x = x_margin + width

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)
        c.setStrokeColor(mark_color)
        c.setLineWidth(lw)

        # Top-left corner
        c.line(left_x, top_y + dist_height, left_x, top_y + dist_height + size)
        c.line(left_x - dist_width, top_y, left_x - dist_width - size, top_y)

        # Top-right corner
        c.line(right_x, top_y + dist_height, right_x, top_y + dist_height + size)
        c.line(right_x + dist_width, top_y, right_x + dist_width + size, top_y)

        # Bottom-left corner
        c.line(left_x, bottom_y - dist_height, left_x, bottom_y - dist_height - size)
        c.line(left_x - dist_width, bottom_y, left_x - dist_width - size, bottom_y)

        # Bottom-right corner
        c.line(right_x, bottom_y - dist_height, right_x, bottom_y - dist_height - size)
        c.line(right_x + dist_width, bottom_y, right_x + dist_width + size, bottom_y)

        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
