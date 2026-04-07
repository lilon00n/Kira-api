# -*- coding: utf-8 -*-
"""
colors_bar.py
Draws filled colored rectangles (a "bar" at multiple intensity levels) for each
spot color at a given position on the PDF.
intensities: comma-separated list of tint values, e.g. "1,0.7,0.5,0.2"
Migrated from PDFlib to reportlab + pypdf.
"""

import json
import os
from color_utils import make_spot_colors
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage


def make(searchpath, pdffile, outfile, colors, intensities, size, x, y, place, sideX, sideY):
    intensities = [float(v) for v in str(intensities).split(',')]
    size = float(size)
    x = float(x)
    y = float(y)

    page_width, page_height, num_pages = get_source_info(pdffile)
    spot_colors = make_spot_colors(colors)

    ret_x = x
    ret_y = y

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)

        cur_x = x
        cur_y = page_height - y

        for color in colors:
            base_spot = spot_colors[color['name']]
            for tint in intensities:
                from reportlab.lib.colors import CMYKColorSep
                tinted = CMYKColorSep(
                    base_spot.cyan * tint,
                    base_spot.magenta * tint,
                    base_spot.yellow * tint,
                    base_spot.black * tint,
                    spotName=base_spot.spotName,
                    density=tint,
                )
                c.setFillColor(tinted)
                c.setStrokeColor(tinted)

                if place in ('T', 'B'):
                    c.rect(cur_x, cur_y - size, size, size, stroke=0, fill=1)
                    cur_x += size
                else:
                    c.rect(cur_x, cur_y - size, size, size, stroke=0, fill=1)
                    cur_y -= size

        ret_x = cur_x
        ret_y = page_height - cur_y

        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
    return json.dumps({'retX': ret_x, 'retY': ret_y})
