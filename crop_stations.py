# -*- coding: utf-8 -*-
"""
crop_stations.py
Draws L-shaped crop marks at multiple station positions on every page.
Each station has its own (xStart, yStart, width, height) in mm.
Migrated from PDFlib to reportlab + pypdf.
"""

from color_utils import get_all_inks_color, make_spot_colors
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage


def _draw_station(c, x_margin, y_margin, width, height, size, dist_w, dist_h, lw):
    """Draw four L-shaped corners for one station rectangle (bottom-up coords)."""
    c.setLineWidth(lw)
    left   = x_margin
    right  = x_margin + width
    top    = y_margin           # already converted to bottom-up by caller
    bottom = y_margin - height

    # Top-left
    c.line(left, top + dist_h,          left, top + dist_h + size)
    c.line(left - dist_w, top,          left - dist_w - size, top)
    # Top-right
    c.line(right, top + dist_h,         right, top + dist_h + size)
    c.line(right + dist_w, top,         right + dist_w + size, top)
    # Bottom-left
    c.line(left, bottom - dist_h,       left, bottom - dist_h - size)
    c.line(left - dist_w, bottom,       left - dist_w - size, bottom)
    # Bottom-right
    c.line(right, bottom - dist_h,      right, bottom - dist_h - size)
    c.line(right + dist_w, bottom,      right + dist_w + size, bottom)


def make(searchpath, pdffile, outfile, colors, stationMarks, size, dist_width, dist_height, weight):
    MM = 72 / 25.4  # points per mm

    size       = float(size)       * MM
    lw         = float(weight)
    dist_w     = float(dist_width) * MM
    dist_h     = float(dist_height) * MM

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)
    mark_color  = get_all_inks_color(spot_colors)   # /Separation /All

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)
        c.setStrokeColor(mark_color)

        for station in stationMarks:
            x_margin = float(station['xStart']) * MM
            y_top    = page_height - float(station['yStart']) * MM
            width    = float(station['width'])  * MM
            height   = float(station['height']) * MM
            _draw_station(c, x_margin, y_top, width, height, size, dist_w, dist_h, lw)

        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
