# -*- coding: utf-8 -*-
"""
micropoint.py
Draws a micropoint: a small Registration-color disc on top of a slightly
larger white disc that acts as a knockout halo.

The white disc ensures the point is visible regardless of the artwork colour
beneath it, while being small enough (0.10–0.18 pt typical radius) not to
affect the final printed result visually.

Position and size come from UI parameters; horizontal placement is typically
at the centre of the job or label, inside the TrimBox.

Migrated from PDFlib to reportlab + pypdf.
"""

from reportlab.lib.colors import white as rl_white
from color_utils import get_registration_color
from pdf_utils import get_source_info, create_overlay_canvas, finalize_and_merge_multipage

# White halo extends this many points beyond the Registration point radius.
# At micropoint scales (0.10–0.18 pt) a fixed 0.05 pt margin is appropriate.
_HALO_EXTRA = 0.05


def _draw_micropoint(c, cx, cy, radius):
    """
    Draw a micropoint centred at (cx, cy).

    Painting order (back to front):
      1. White disc  — radius + _HALO_EXTRA  — knocks out artwork beneath
      2. /All disc   — radius                — Registration, prints on every plate

    radius: final radius of the Registration point in points (typ. 0.10–0.18).
    """
    # 1. White knockout — slightly larger, painted first (behind)
    c.setFillColor(rl_white)
    c.circle(cx, cy, radius + _HALO_EXTRA, stroke=0, fill=1)

    # 2. Registration color point — on top
    c.setFillColor(get_registration_color())
    c.circle(cx, cy, radius, stroke=0, fill=1)


def make(searchpath, pdffile, outfile, colors, x, y, crop_size):
    x         = float(x)
    y         = float(y)
    radius    = float(crop_size)   # used directly as pt radius — no Bézier conversion

    page_width, page_height, num_pages = get_source_info(pdffile)

    # y is measured from the top in the original coordinate system
    cy = page_height - y

    pages_overlays = []
    for _ in range(num_pages):
        c, buf = create_overlay_canvas(page_width, page_height)
        _draw_micropoint(c, x, cy, radius)
        c.showPage()
        pages_overlays.append((c, buf))

    finalize_and_merge_multipage(pdffile, pages_overlays, outfile)
