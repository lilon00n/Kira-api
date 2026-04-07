# -*- coding: utf-8 -*-
"""
one_up.py
Creates a single "one-up proof sheet" PDF:
  - A new page larger than the source, with space for a label band
  - The source PDF embedded at an offset (bleed/trim registration)
  - A label band: Nala logo, client logo, colour table, job info, machine/material, salida image
  - Crop marks, registration marks, and dimension cotas in the margins
  - Extra pages for each separation TIFF

Migrated from PDFlib to reportlab + pypdf + Pillow.
"""

import io
import json
import os

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
from reportlab.lib.colors import black, white, CMYKColor, CMYKColorSep
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas

from clients import findClient
from color_utils import make_spot_colors, get_all_inks_color

# ---------------------------------------------------------------------------
# Constants (mirroring original)
# ---------------------------------------------------------------------------
POINT_TO_MM = 72 / 25.4          # points per mm
CROP_SIZE         = 8             # mm
SQUARE_COLOR_SIZE = 7             # pt
FONT_SIZE         = 8             # pt
FONT_NAME         = 'Helvetica'
CROP_MARK_SEP     = 4             # pt
COTA_SEP          = 5  * POINT_TO_MM
CRUZ_SEP          = 3  * POINT_TO_MM
BLEED_EXCESS      = 5  * POINT_TO_MM
CROP_EXCESS       = CROP_SIZE * POINT_TO_MM
MEDIA_EXCESS      = 5  * POINT_TO_MM
DATA_PATH         = os.path.join(os.path.dirname(__file__), 'data')

# Label column titles & matching info-dict keys
TITLES = [
    'Cliente:', 'Vendedor:', 'Esp. técnica:', 'Archivo:',
    'Tipo de producto:', 'Tipo de código:', 'No. Barras', 'Diseñador',
]
KEYS = [
    'customer', 'salesman', 'tsCode', 'fileName',
    'productType', 'barcodeType', 'barcodeNumber', 'designer',
]

# ---------------------------------------------------------------------------
# Text-measurement helpers (replace PDFlib info_textline / info_image)
# ---------------------------------------------------------------------------
TEXT_HEIGHT = FONT_SIZE * 1.35    # approximate cap+descender height in points

# Maximum width (pt) reserved for a color name in the label band.
# If any name is wider, it gets abbreviated automatically.
MAX_COLOR_NAME_WIDTH = 72   # ~25.4 mm — comfortable for an A4 label


def _abbreviate_pantone(name: str) -> str:
    """Shorten Pantone names for compact display in tight layouts.

    'PANTONE 261 C'  →  'P261 C'
    'Pantone 192 C'  →  'P192 C'
    'Black'          →  'Black'   (unchanged)
    """
    import re
    m = re.match(r'(?i)pantone\s+(.+)', name.strip())
    if m:
        return 'P' + m.group(1)
    return name


def _display_name(name: str) -> str:
    """Return display name for a colour — abbreviated if it would be too wide."""
    if pdfmetrics.stringWidth(name, FONT_NAME, FONT_SIZE) > MAX_COLOR_NAME_WIDTH:
        return _abbreviate_pantone(name)
    return name


def _tw(text, fsize=FONT_SIZE):
    """StringWidth in points using Helvetica."""
    return pdfmetrics.stringWidth(str(text), FONT_NAME, fsize)


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def _get_bleed_trim_gap(boxes):
    return float(boxes['bleed'][0]) - float(boxes['trim'][0]), \
           float(boxes['bleed'][1]) - float(boxes['trim'][1])


def _get_trim_size(boxes):
    return (float(boxes['trimWidth'])  * POINT_TO_MM,
            float(boxes['trimHeight']) * POINT_TO_MM)


def _get_label_height(colors, info, nala_h, logo_h):
    mat_mach = info.get('materialMachines', [])
    col_h    = len(colors)         * (TEXT_HEIGHT + 8)
    mm_h     = len(mat_mach) * 2   * (TEXT_HEIGHT + 4)
    inf_h    = len(TITLES)         * (TEXT_HEIGHT + 4)
    return max(nala_h + 10 + logo_h, inf_h, col_h, mm_h) + 10


def _get_label_width(colors, info, logo_w):
    mat_mach = info.get('materialMachines', [])
    max_col  = max((_tw(_display_name(c['name'])) for c in colors), default=0)
    max_pct  = _tw('100.00%  ')
    max_inf  = max((_tw(info.get(k, '')) for k in KEYS), default=0)
    max_mach = max(
        (max(_tw(mm.get('machine', '')), _tw(mm.get('material', '')))
         for mm in mat_mach),
        default=0,
    )
    total_col   = max_col + 10 + SQUARE_COLOR_SIZE * 2 + max_pct
    total_info  = _tw(' Tipo de producto:') + 15 + max_inf
    total_mach  = _tw('Maquina:') + 10 + max_mach
    total_sal   = _tw('Salida:') + 25
    return logo_w + total_col + total_info + total_mach + total_sal


# ---------------------------------------------------------------------------
# Drawing helpers (all draw onto a ReportLab Canvas)
# ---------------------------------------------------------------------------

def _draw_crop_marks(c, x_margin, y_margin, size, weight, dh, dw, w, h):
    """Draw 4 L-shaped crop-mark corners."""
    c.setStrokeColor(black)
    c.setLineWidth(weight)
    top    = y_margin
    bottom = y_margin - h
    left   = x_margin
    right  = x_margin + w
    # Top-left
    c.line(left,  top + dh,        left,  top + dh + size)
    c.line(left - dw, top,         left - dw - size, top)
    # Top-right
    c.line(right, top + dh,        right, top + dh + size)
    c.line(right + dw, top,        right + dw + size, top)
    # Bottom-left
    c.line(left,  bottom - dh,     left,  bottom - dh - size)
    c.line(left - dw, bottom,      left - dw - size, bottom)
    # Bottom-right
    c.line(right, bottom - dh,     right, bottom - dh - size)
    c.line(right + dw, bottom,     right + dw + size, bottom)


def _draw_one_reg_mark(c, cx, cy, radius):
    """Cross + concentric circles registration mark."""
    c.setStrokeColor(black)
    c.setFillColor(black)
    c.setLineWidth(0.5)
    c.line(cx - radius, cy, cx + radius, cy)
    c.line(cx, cy - radius, cx, cy + radius)
    c.circle(cx, cy, radius / 3, stroke=0, fill=1)
    c.setStrokeColor(white)
    c.setLineWidth(0.5)
    c.line(cx - radius / 3, cy, cx + radius / 3, cy)
    c.line(cx, cy - radius / 3, cx, cy + radius / 3)
    c.setStrokeColor(black)
    c.circle(cx, cy, 2 * radius / 3, stroke=1, fill=0)


def _draw_registration_marks(c, label_height, boxes, add_info):
    trim_w, trim_h = _get_trim_size(boxes)
    cx = MEDIA_EXCESS + CROP_EXCESS + add_info + trim_w / 2
    cy = MEDIA_EXCESS + label_height + CROP_EXCESS + trim_h / 2
    r  = 5

    top_y    = MEDIA_EXCESS + label_height + CROP_EXCESS + trim_h + CROP_MARK_SEP + TEXT_HEIGHT / 2 + CRUZ_SEP
    bottom_y = MEDIA_EXCESS + label_height + CROP_EXCESS - CROP_MARK_SEP - TEXT_HEIGHT / 2 - CRUZ_SEP
    left_x   = MEDIA_EXCESS + CROP_EXCESS + add_info - CROP_MARK_SEP - TEXT_HEIGHT / 2 - CRUZ_SEP
    right_x  = MEDIA_EXCESS + CROP_EXCESS + add_info + trim_w + CROP_MARK_SEP + TEXT_HEIGHT / 2 + CRUZ_SEP

    for px, py in [(cx, top_y), (cx, bottom_y), (left_x, cy), (right_x, cy)]:
        _draw_one_reg_mark(c, px, py, r)


def _draw_cotas(c, label_height, boxes, add_info):
    trim_w, trim_h = _get_trim_size(boxes)
    cx = MEDIA_EXCESS + CROP_EXCESS + add_info + trim_w / 2
    cy = MEDIA_EXCESS + CROP_EXCESS + label_height + trim_h / 2

    cota_x = str(round(float(boxes['trimWidth']),  3)) + 'mm'
    cota_y = str(round(float(boxes['trimHeight']), 3)) + 'mm'
    cota_xw = _tw(cota_x)
    cota_yw = _tw(cota_y)

    # ---- Horizontal cota (above trim) ----
    start_x = MEDIA_EXCESS + CROP_EXCESS + add_info
    start_y = MEDIA_EXCESS + label_height + CROP_EXCESS + trim_h + COTA_SEP
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.line(start_x, start_y, start_x + trim_w, start_y)
    # White background behind text
    c.setFillColor(white)
    c.rect(cx - cota_xw / 2, start_y, cota_xw, TEXT_HEIGHT, stroke=0, fill=1)
    c.setFillColor(black)
    c.setFont(FONT_NAME, FONT_SIZE)
    c.drawString(cx - cota_xw / 2, start_y, cota_x)

    # ---- Vertical cota (left of trim) ----
    lx = MEDIA_EXCESS + CROP_EXCESS + add_info - COTA_SEP
    c.line(lx, MEDIA_EXCESS + label_height + CROP_EXCESS,
           lx, MEDIA_EXCESS + label_height + CROP_EXCESS + trim_h)
    c.setFillColor(white)
    c.rect(lx - TEXT_HEIGHT, cy - cota_yw / 2, TEXT_HEIGHT, cota_yw, stroke=0, fill=1)
    c.saveState()
    c.translate(lx - TEXT_HEIGHT, cy - cota_yw / 2)
    c.rotate(90)
    c.setFillColor(black)
    c.drawString(0, 0, cota_y)
    c.restoreState()


def _draw_colors_section(c, x0, y0, colors, spot_colors, max_logo):
    """Draw colour swatches + names + ink coverage column. Returns new x."""
    max_col_w = max((_tw(_display_name(col['name'])) for col in colors), default=0)
    x = x0 + max_col_w
    y = y0
    max_pct = _tw('100.00%  ')

    for i, color in enumerate(colors):
        spot = spot_colors[color['name']]
        name = _display_name(color['name'])
        ink_cov = str(color.get('inkCov', '')) + '%'

        # Colour name (right-aligned to x)
        c.setFillColor(spot)
        c.setFont(FONT_NAME, FONT_SIZE)
        nw = _tw(name)
        c.drawString(x - nw, y, name)

        # Ink coverage %
        c.setFillColor(black)
        c.drawString(x + 20, y, ink_cov)

        # 4 swatch boxes: 100%, 70%, 50%, 20%
        for j, tint in enumerate([1.0, 0.7, 0.5, 0.2]):
            tinted = CMYKColorSep(
                spot.cyan * tint, spot.magenta * tint,
                spot.yellow * tint, spot.black * tint,
                spotName=spot.spotName, density=tint,
            )
            c.setFillColor(tinted)
            bx = x + 2 + (j % 2) * SQUARE_COLOR_SIZE
            by = y if j >= 2 else y + 4
            c.rect(bx, by, SQUARE_COLOR_SIZE, 4, stroke=0, fill=1)

        # Separator line
        c.setStrokeColor(black)
        c.setLineWidth(0.3)
        x_sep_start = 2 * CROP_SIZE * POINT_TO_MM + max_logo
        x_sep_end   = x + SQUARE_COLOR_SIZE * 2 + max_pct
        c.line(x_sep_start, y - 2, x_sep_end, y - 2)

        y -= TEXT_HEIGHT + 8

    return x


def _draw_info_section(c, x0, y0, info):
    """Draw the job-info key/value rows. Returns new x."""
    max_key = _tw(' Tipo de producto:')
    max_val = max((_tw(str(info.get(k, ''))) for k in KEYS), default=0)
    x = x0 + SQUARE_COLOR_SIZE * 2 + _tw('100.00%  ') + 5 + max_key
    y = y0

    c.setStrokeColor(black)
    c.setFillColor(black)
    c.setFont(FONT_NAME, FONT_SIZE)

    for i, key in enumerate(KEYS):
        title = TITLES[i]
        value = str(info.get(key, ''))
        tw_title = _tw(title)
        c.drawString(x - tw_title, y, title)
        c.setLineWidth(0.3)
        c.line(x - tw_title, y - 2, x, y - 2)
        c.drawString(x + 2, y, value)
        y -= TEXT_HEIGHT + 4

    return x + max_val + max_key


def _draw_machine_section(c, x0, y0, info):
    """Draw machine/material rows. Returns new x."""
    mat_mach  = info.get('materialMachines', [])
    max_mach  = max(
        (max(_tw(mm.get('machine', '')), _tw(mm.get('material', '')))
         for mm in mat_mach),
        default=0,
    )
    key_w = _tw('Maquina:')
    x = x0
    y = y0

    c.setFillColor(black)
    c.setFont(FONT_NAME, FONT_SIZE)
    c.setStrokeColor(black)

    for mm in mat_mach:
        c.drawString(x - key_w, y, 'Maquina:')
        c.setLineWidth(0.3)
        c.line(x - key_w, y - 2, x, y - 2)
        c.drawString(x + 2, y, mm.get('machine', ''))
        y -= TEXT_HEIGHT + 4

        mat_kw = _tw('Material:')
        c.drawString(x - mat_kw, y, 'Material:')
        c.line(x - mat_kw, y - 2, x, y - 2)
        c.drawString(x + 2, y, mm.get('material', ''))
        y -= TEXT_HEIGHT + 4

    return x + max_mach


def _draw_salida_section(c, x0, y0, salida):
    """Draw salida label + image."""
    sal_w = _tw('Salida:')
    c.setFillColor(black)
    c.setFont(FONT_NAME, FONT_SIZE)
    c.drawString(x0 + sal_w, y0, 'Salida:')
    img_path = os.path.join(DATA_PATH, 'embobinado', salida + '.png')
    if os.path.exists(img_path):
        try:
            img_h = 25 * 0.25  # approximate
            c.drawImage(img_path, x0 + sal_w, y0 - TEXT_HEIGHT - img_h - 4,
                        width=25, height=25, preserveAspectRatio=True)
        except Exception:
            pass  # image missing – skip gracefully


# ---------------------------------------------------------------------------
# Main make() function
# ---------------------------------------------------------------------------

def make(searchpath, pdffile, outfile, client, boxes, colorsJson, info,
         separations_folder, path_images, names):
    client_obj, title, boxes, info = _load_body_info(client, outfile, boxes, info)

    spot_colors = make_spot_colors(colorsJson)

    # ---- Measure Nala logo dimensions from its PDF ----
    nala_pdf_path = os.path.join(DATA_PATH, 'nala-rotulo.pdf')
    nala_reader   = PdfReader(nala_pdf_path)
    nala_h = float(nala_reader.pages[0].mediabox.height) * 0.6
    nala_w = float(nala_reader.pages[0].mediabox.width)  * 0.6

    # ---- Measure client logo ----
    logo_path = client_obj.logo
    logo_w = 0
    logo_h = 0
    if os.path.exists(logo_path):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(logo_path)
            iw, ih = img.size          # pixels
            # Scale factor 0.05 → approximate pt size (72 pt/in, 96 dpi assumed)
            logo_w = iw * 72 / 96 * 0.05
            logo_h = ih * 72 / 96 * 0.05
        except Exception:
            logo_w, logo_h = 30, 10   # safe fallback

    # ---- Get source PDF dimensions ----
    src_reader  = PdfReader(pdffile)
    src_w = float(src_reader.pages[0].mediabox.width)
    src_h = float(src_reader.pages[0].mediabox.height)

    # ---- Layout calculations ----
    desp_x, desp_y = _get_bleed_trim_gap(boxes)
    trim_w, trim_h = _get_trim_size(boxes)
    max_logo_w = max(nala_w, logo_w)          # Nala logo is usually wider than client logo
    label_h = _get_label_height(colorsJson, info, nala_h, logo_h)
    label_w = _get_label_width(colorsJson, info, max_logo_w)
    total_w  = max(label_w, trim_w)
    add_info = (label_w - trim_w) / 2 if label_w > trim_w else 0

    media_w  = total_w  + CROP_EXCESS * 2 + MEDIA_EXCESS * 2
    media_h  = trim_h   + label_h + CROP_EXCESS * 2 + MEDIA_EXCESS * 2

    # Position of the source PDF bottom-left corner inside the output page
    offset_x = MEDIA_EXCESS + CROP_EXCESS + add_info + desp_x
    offset_y = MEDIA_EXCESS + label_h + CROP_EXCESS + desp_y

    # ---- Build the output PDF ----
    writer = PdfWriter()

    # Strategy for Artpro compatibility:
    # Artpro+ requires artwork to remain as NATIVE PAGE CONTENT at its original
    # coordinates. Any wrapping in Form XObjects (what merge_transformed_page and
    # even add_transformation can cause indirectly) makes Artpro show a blank page.
    #
    # Instead of moving the artwork, we EXPAND THE PAGE in the negative Y direction
    # so the label band sits below the artwork in page-coordinate space.
    # The MediaBox lower-left is shifted to (−margin−label, 0) and the artwork
    # content stream is left completely untouched.
    #
    # Layout:
    #   Y = src_h + margin_top         ← top edge of ET sheet
    #   Y = src_h                      ← top of source artwork (original coords)
    #   Y = 0                          ← bottom of source artwork (original coords, unchanged)
    #   Y = -label_h - margin_bottom   ← bottom of label band
    #
    # The MediaBox covers the full extent: lower-left = (artwork_left, -(label_h+margin))
    # The artwork is placed at its original position — no cm transform injected.

    src_page = src_reader.pages[0]
    # Original source coordinates: artwork occupies (0,0)→(src_w, src_h)
    # We need to shift the left edge when label_w > src_w
    art_x0 = add_info   # horizontal offset of artwork within ET (may be 0)
    art_y0 = 0          # artwork bottom stays at Y=0 in content-stream space

    # MediaBox in content-stream space:
    #   left:   art_x0 - MEDIA_EXCESS - CROP_EXCESS
    #   right:  art_x0 + src_w + MEDIA_EXCESS + CROP_EXCESS   (or label_w edge)
    #   bottom: -(label_h + CROP_EXCESS + MEDIA_EXCESS)
    #   top:    src_h + MEDIA_EXCESS + CROP_EXCESS
    mb_left   = art_x0 - (MEDIA_EXCESS + CROP_EXCESS)
    mb_right  = mb_left + media_w
    mb_bottom = -(label_h + CROP_EXCESS + MEDIA_EXCESS)
    mb_top    = src_h + CROP_EXCESS + MEDIA_EXCESS

    # Append the source page verbatim — content stream untouched
    writer.append(src_reader, pages=[0])
    main_page = writer.pages[0]

    # Expand the MediaBox to cover the full ET sheet; artwork content stays at Y=0
    main_page.mediabox = RectangleObject((float(mb_left), float(mb_bottom),
                                          float(mb_right), float(mb_top)))
    # Remove box overrides from the source page that would restrict the visible area
    for _bk in ('/BleedBox', '/CropBox', '/ArtBox', '/TrimBox'):
        if _bk in main_page:
            del main_page[_bk]

    # Recalculate drawing offsets for all label elements:
    # In ET-sheet space (origin = mb_left, mb_bottom), coordinates are:
    #   artwork_bottom_left = (art_x0 - mb_left, 0 - mb_bottom)
    # For drawing functions that use bottom-left = (0,0) convention:
    #   x_draw_offset = art_x0 - mb_left = MEDIA_EXCESS + CROP_EXCESS
    #   y_draw_offset = -mb_bottom = label_h + CROP_EXCESS + MEDIA_EXCESS
    #
    # The ReportLab canvas is drawn in absolute content-stream space,
    # but the canvas pagesize covers the MediaBox extent starting from (0,0).
    # We set the canvas origin at (mb_left, mb_bottom) by using a full-size
    # canvas and offsetting all drawing operations by (-mb_left, -mb_bottom).

    # Canvas pagesize = MediaBox size (but canvas origin is (0,0), not mb coords)
    canvas_w = float(mb_right - mb_left)
    canvas_h = float(mb_top   - mb_bottom)
    # Shift to convert from MB-relative coords to canvas coords:
    cx_off = -mb_left    # add to any mb_x to get canvas_x
    cy_off = -mb_bottom  # add to any mb_y to get canvas_y

    # In the canvas, artwork sits at:
    #   canvas_x = art_x0 + cx_off = art_x0 - mb_left = MEDIA_EXCESS + CROP_EXCESS
    #   canvas_y = 0      + cy_off = -mb_bottom = label_h + CROP_EXCESS + MEDIA_EXCESS
    art_canvas_x = art_x0 + cx_off
    art_canvas_y = 0      + cy_off   # = label_h + CROP_EXCESS + MEDIA_EXCESS

    # ---- Draw the label overlay with ReportLab ----
    # The ReportLab canvas uses (0,0) at the bottom-left of the canvas page.
    # canvas_w == media_w and canvas_h == media_h so all existing drawing
    # helper coordinate formulas remain valid: "MEDIA_EXCESS + label_h + CROP_EXCESS"
    # in canvas space equals art_canvas_y, matching the artwork's original bottom edge.
    label_buf = io.BytesIO()
    c = Canvas(label_buf, pagesize=(canvas_w, canvas_h))
    c.setFont(FONT_NAME, FONT_SIZE)

    # Nala logo position (canvas coords = same as old ET sheet coords)
    nala_x = MEDIA_EXCESS + CROP_EXCESS
    nala_y = MEDIA_EXCESS + label_h - nala_h

    # Client logo image
    logo_x = MEDIA_EXCESS + CROP_EXCESS
    logo_y = MEDIA_EXCESS + label_h - nala_h - 10 - logo_h
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, logo_x, logo_y,
                        width=logo_w, height=logo_h, preserveAspectRatio=True)
        except Exception:
            pass

    # Crop marks
    crop_m_y = MEDIA_EXCESS + label_h + CROP_EXCESS + trim_h
    _draw_crop_marks(
        c,
        MEDIA_EXCESS + CROP_EXCESS + add_info,
        crop_m_y,
        CROP_SIZE * POINT_TO_MM, 0.01,
        0, 0,
        trim_w, trim_h,
    )

    # Registration marks
    _draw_registration_marks(c, label_h, boxes, add_info)

    # Cotas
    _draw_cotas(c, label_h, boxes, add_info)

    # ---- Colour section ----
    x_gen = MEDIA_EXCESS + CROP_EXCESS + max_logo_w + 10
    y_gen = MEDIA_EXCESS + label_h - 10
    x_gen = _draw_colors_section(c, x_gen, y_gen, colorsJson, spot_colors, max_logo_w)

    # ---- Info section ----
    x_gen = _draw_info_section(c, x_gen, y_gen, info)

    # ---- Machine section ----
    x_gen = _draw_machine_section(c, x_gen, y_gen, info)

    # ---- Salida section ----
    salida = info.get('salida', '')
    if salida:
        _draw_salida_section(c, x_gen, y_gen, salida)

    c.showPage()
    c.save()

    # Merge label overlay onto the main page.
    # The label canvas uses coordinates where y=0 is canvas bottom = ET sheet bottom.
    # The main page has artwork at y=0 (artwork origin), with label band at y<0.
    # We translate the canvas by (mb_left, mb_bottom) so canvas y=MEDIA_EXCESS maps
    # to page y = mb_bottom + MEDIA_EXCESS = -CROP_EXCESS - label_h (label band area).
    label_buf.seek(0)
    label_reader = PdfReader(label_buf)
    main_page.merge_transformed_page(
        label_reader.pages[0],
        Transformation().translate(tx=float(mb_left), ty=float(mb_bottom)),
    )

    # Merge the Nala logo PDF at the correct canvas position
    nala_reader2  = PdfReader(nala_pdf_path)
    nala_src_page = nala_reader2.pages[0]
    scale = 0.6
    main_page.merge_transformed_page(
        nala_src_page,
        Transformation().scale(scale, scale).translate(
            tx=nala_x, ty=nala_y,
        ),
    )
    # Strip Nala logo spot colors from parent page resources
    _strip_foreign_colorspaces(main_page, [col['name'] for col in colorsJson])

    # TrimBox = artwork area on the ET sheet (in MediaBox coords; artwork at Y=0)
    art_mb_x0 = float(art_x0)
    art_mb_y0 = 0.0
    art_mb_x1 = float(art_x0 + src_w)
    art_mb_y1 = float(src_h)
    main_page.trimbox = RectangleObject((art_mb_x0, art_mb_y0, art_mb_x1, art_mb_y1))

    # ---- Separation pages ----
    for index, image_name in enumerate(path_images):
        img_path = separations_folder + image_name
        sep_h    = src_h + 10

        sep_buf = io.BytesIO()
        sep_c   = Canvas(sep_buf, pagesize=(src_w, sep_h))
        sep_c.drawImage(img_path, 0, 10, width=src_w, height=src_h,
                        preserveAspectRatio=True)
        sep_c.setFont('Helvetica', 10)
        sep_c.setFillColor(black)
        sep_c.drawString(0, 0, names[index])
        sep_c.showPage()
        sep_c.save()

        sep_buf.seek(0)
        sep_reader = PdfReader(sep_buf)
        writer.add_page(sep_reader.pages[0])
        print(image_name)

    with open(outfile, 'wb') as f:
        writer.write(f)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _strip_foreign_colorspaces(page, job_spot_names):
    """
    Remove /Separation colorspace entries from the page resources that do NOT
    belong to the job's ink list. Entries added by merged template elements
    (e.g. the Nala logo PDF) are stripped so that separation-preview tools
    show only the actual job inks.

    Safe because pypdf's merge_transformed_page wraps foreign pages in Form
    XObjects that carry their own self-contained /Resources, so the logo still
    renders correctly after the parent-page entries are removed.
    """
    allowed = set(job_spot_names) | {'All'}
    try:
        res = page['/Resources']
        if '/ColorSpace' not in res:
            return
        cs_dict = res['/ColorSpace']
        to_remove = []
        for key in list(cs_dict.keys()):
            try:
                cs_arr = list(cs_dict[key])
                if len(cs_arr) >= 2 and str(cs_arr[0]) == '/Separation':
                    spot_name = str(cs_arr[1]).lstrip('/')
                    if spot_name not in allowed:
                        to_remove.append(key)
            except Exception:
                pass
        for key in to_remove:
            del cs_dict[key]
    except Exception:
        pass


def _load_body_info(client, outfile, boxes, info):
    client_obj = findClient(client)
    sep = '\\' if '\\' in outfile else '/'
    title = outfile.split(sep)[-1]
    info  = json.loads(info)  if isinstance(info,  str) else info
    boxes = json.loads(boxes) if isinstance(boxes, str) else boxes
    return client_obj, title, boxes, info
