# -*- coding: utf-8 -*-
"""
circles.py
Draws concentric stroke circles for each spot color, stacking them along
a T/B/L/R axis from a starting position.
Migrated from PDFlib to reportlab + pypdf.
"""

import json
import os
from color_utils import make_spot_colors
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage


# Original used arcs with radii 0.1+0.6*i for i in range(1,16)
_RADII = [0.1 + 0.6 * i for i in range(1, 16)]
OUTER_RADIUS = _RADII[-1]  # 0.1 + 0.6*15 = 9.1


def _draw_concentric(c, cx, cy, spot_color):
    c.setStrokeColor(spot_color)
    c.setLineWidth(0.24)
    for r in _RADII:
        c.circle(cx, cy, r, stroke=1, fill=0)


def make(searchpath, pdffile, outfile, x, y, colors, place, sideX, sideY):
    x = float(x)
    y = float(y)
    radius = OUTER_RADIUS

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)

    ret_x = -1
    ret_y = -1

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)

        # Original uses topdown=true so y is from top; convert
        cur_y = page_height - y

        # Apply initial offset based on placement corner
        if place in ('TL', 'BL'):
            cur_x = x - radius
        else:
            cur_x = x + radius

        if place in ('TL', 'TR'):
            cur_y = cur_y + radius
        else:
            cur_y = cur_y - radius

        for color in colors:
            spot = spot_colors[color['name']]
            _draw_concentric(c, cur_x, cur_y, spot)

            if place in ('TL', 'TR'):
                cur_y = cur_y + (radius * 2)
            else:
                cur_y = cur_y - (radius * 2)

        if place in ('TL', 'TR'):
            ret_y = cur_y + radius
        else:
            ret_y = cur_y - radius

        ret_x = cur_x + radius * 2

        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
    return json.dumps({'retX': ret_x, 'retY': page_height - ret_y})
