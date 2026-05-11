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
from reportlab.lib.colors import white, CMYKColor, CMYKColorSep
black        = CMYKColor(0, 0, 0, 1)          # 100 % K — never RGB, never process build
registration = CMYKColorSep(1, 1, 1, 1, spotName='All', density=1.0)  # /Separation /All — prints on every separation
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
BLEED_ET_MM       = 5                        # mm — editable bleed around TrimBox in ET sheet
BLEED_EXCESS      = BLEED_ET_MM * POINT_TO_MM
CROP_EXCESS       = CROP_SIZE * POINT_TO_MM
MEDIA_EXCESS      = 10 * POINT_TO_MM         # 10mm outer margin (MediaBox boundary)
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
    logos_h  = nala_h + (10 if nala_h > 0 and logo_h > 0 else 0) + logo_h
    return max(logos_h, inf_h, col_h, mm_h) + 10


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
    c.setStrokeColor(registration)
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
    c.setStrokeColor(registration)
    c.setFillColor(registration)
    c.setLineWidth(0.5)
    c.line(cx - radius, cy, cx + radius, cy)
    c.line(cx, cy - radius, cx, cy + radius)
    c.circle(cx, cy, radius / 3, stroke=0, fill=1)
    c.setStrokeColor(white)
    c.setLineWidth(0.5)
    c.line(cx - radius / 3, cy, cx + radius / 3, cy)
    c.line(cx, cy - radius / 3, cx, cy + radius / 3)
    c.setStrokeColor(registration)
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
    c.setStrokeColor(registration)
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
    c.setStrokeColor(registration)
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
         page_index=0, separations_folder=None, path_images=None, names=None, logo_path=None):
    client_obj, title, boxes, info = _load_body_info(client, outfile, boxes, info)

    # Override client logo if a custom path was provided and the file exists
    if logo_path and os.path.exists(logo_path):
        client_obj.logo = logo_path

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
            raw_w_pt = iw * 72 / 96    # natural width in points (72pt/in, 96dpi)
            raw_h_pt = ih * 72 / 96    # natural height in points
            MAX_LOGO_H = 25            # cap at ~8.8mm so it fits the label band
            scale = min(1.0, MAX_LOGO_H / raw_h_pt) if raw_h_pt > 0 else 1.0
            logo_w = raw_w_pt * scale
            logo_h = raw_h_pt * scale
        except Exception:
            logo_w, logo_h = 40, 20   # safe fallback

    # Si el cliente tiene logo propio, suprimir el logo de Nala
    if logo_h > 0:
        nala_h = 0
        nala_w = 0

    # ---- Get source PDF dimensions ----
    src_reader  = PdfReader(pdffile)
    src_w = float(src_reader.pages[page_index].mediabox.width)
    src_h = float(src_reader.pages[page_index].mediabox.height)

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
    # Strategy: keep artwork INLINE in the page content stream (no Form XObject).
    # All spot colors (CS0..CS4), ExtGState, and nested XObjects (Fm0..Fm117)
    # stay at page level — exactly like marcas.pdf — so Artpro+ can enumerate
    # separations correctly.  Artwork is positioned via a q/cm/Q block.
    import re
    from pypdf.generic import DecodedStreamObject, NameObject, ArrayObject

    writer = PdfWriter()
    writer.append(src_reader, pages=[page_index])
    main_page = writer.pages[0]

    # Record ALL spot-channel names from the source AI colorspaces.
    # Used for diagnostics / future reference; no stripping is performed.
    _src_res = main_page[NameObject('/Resources')].get_object()
    _src_cs_raw = _src_res.get('/ColorSpace')
    _src_cs_dict = _src_cs_raw.get_object() if _src_cs_raw is not None else {}
    _src_spot_names = set()
    for _cs_val in _src_cs_dict.values():
        try:
            _cs_arr = _cs_val.get_object()
            if hasattr(_cs_arr, '__getitem__') and len(_cs_arr) >= 2:
                if str(_cs_arr[0]) == '/Separation':
                    _src_spot_names.add(str(_cs_arr[1]).lstrip('/'))
        except Exception:
            pass

    # Positive ET-sheet MediaBox
    main_page.mediabox = RectangleObject((0.0, 0.0, float(media_w), float(media_h)))
    for _bk in ('/BleedBox', '/CropBox', '/ArtBox', '/TrimBox'):
        if _bk in main_page:
            del main_page[_bk]

    # Extract raw content bytes from the ORIGINAL source reader — NOT from the
    # writer's clone.  In pypdf >=4 the lazy-clone mechanism can return the
    # still-compressed (FlateDecode) bytes when get_data() is called on a
    # writer-side stream object.  If that happens the OC-strip regex finds no
    # matches (binary compressed data), the compressed bytes get wrapped in the
    # q/cm/Q block, and PDF readers cannot parse the content stream →
    # artwork area appears blank while the label band still renders correctly.
    _src_page_orig = src_reader.pages[page_index]
    _contents_obj = _src_page_orig[NameObject('/Contents')].get_object()
    if isinstance(_contents_obj, ArrayObject):
        _raw_art = b'\n'.join(ref.get_object().get_data() for ref in _contents_obj)
    else:
        _raw_art = _contents_obj.get_data()

    # Strip Optional Content Group markers (/OC /MCx BDC ... EMC).
    # The entire AI artwork is wrapped in one OC group (MC0).  Artpro+ treats
    # marked content as optional layers; without /OCProperties in the catalog
    # it defaults the group to OFF and deletes the content → blank page.
    # BDC/EMC markers are purely informational and do not affect graphics state,
    # so stripping them makes the artwork unconditionally visible.
    _raw_art = re.sub(rb'/OC\s+/\w+\s+BDC\s*', b'', _raw_art)
    _raw_art = re.sub(rb'\bEMC\b\s*', b'', _raw_art)

    # If the source PDF was cropped in place (e.g. set_trimbox_from_separation),
    # its visible box can start at a non-zero origin. Subtract that origin so the
    # artwork lands centered on the ET sheet instead of keeping the old page offset.
    _src_view_box = _src_page_orig.cropbox or _src_page_orig.mediabox
    _src_x0 = float(_src_view_box.left)
    _src_y0 = float(_src_view_box.bottom)

    # Wrap artwork in q/cm/Q so it renders at the ET artwork origin.
    # Resources (CS0..CS4, Fm0..Fm117, etc.) stay at page level — Artpro+ requires this.
    _header = f'q\n1 0 0 1 {offset_x - _src_x0:.6f} {offset_y - _src_y0:.6f} cm\n'.encode()
    _wrapped = _header + _raw_art + b'\nQ\n/CropFm Do\n'
    # flate_encode() compresses the stream and sets /Filter /FlateDecode explicitly,
    # which avoids pypdf length-calculation quirks for DecodedStreamObject.
    _new_stream = DecodedStreamObject()
    _new_stream.set_data(_wrapped)
    _new_stream = _new_stream.flate_encode()
    _new_ref = writer._add_object(_new_stream)
    main_page[NameObject('/Contents')] = _new_ref

    canvas_w = float(media_w)
    canvas_h = float(media_h)

    # ---- Crop marks — separate FormXObject, survives strip_footprint.py ----
    crop_m_y = MEDIA_EXCESS + label_h + CROP_EXCESS + trim_h
    crop_buf  = io.BytesIO()
    crop_c    = Canvas(crop_buf, pagesize=(canvas_w, canvas_h))
    _draw_crop_marks(
        crop_c,
        MEDIA_EXCESS + CROP_EXCESS + add_info,
        crop_m_y,
        CROP_SIZE * POINT_TO_MM, 0.01,
        0, 0,
        trim_w, trim_h,
    )
    crop_c.showPage()
    crop_c.save()

    # ---- Draw label overlay with ReportLab at standard ET coordinates ----
    # All drawing helpers use positive ET-sheet coords:
    #   y=MEDIA_EXCESS → label band bottom
    #   y=MEDIA_EXCESS+label_h+CROP_EXCESS → artwork bottom in ET space
    # merge_page() merges inline (no Form XObject), identity transform (no shift needed).
    label_buf = io.BytesIO()
    c = Canvas(label_buf, pagesize=(canvas_w, canvas_h))
    c.setFont(FONT_NAME, FONT_SIZE)

    nala_x = MEDIA_EXCESS + CROP_EXCESS
    nala_y = MEDIA_EXCESS + label_h - nala_h

    logo_x = MEDIA_EXCESS + CROP_EXCESS
    if nala_h > 0:
        logo_y = MEDIA_EXCESS + label_h - nala_h - 10 - logo_h
    else:
        logo_y = MEDIA_EXCESS + label_h - 5 - logo_h
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, logo_x, logo_y,
                        width=logo_w, height=logo_h, preserveAspectRatio=True)
        except Exception:
            pass

    _draw_registration_marks(c, label_h, boxes, add_info)
    _draw_cotas(c, label_h, boxes, add_info)

    x_gen = MEDIA_EXCESS + CROP_EXCESS + max_logo_w + 10
    y_gen = MEDIA_EXCESS + label_h - 10
    x_gen = _draw_colors_section(c, x_gen, y_gen, colorsJson, spot_colors, max_logo_w)
    x_gen = _draw_info_section(c, x_gen, y_gen, info)
    x_gen = _draw_machine_section(c, x_gen, y_gen, info)
    salida = info.get('salida', '')
    if salida:
        _draw_salida_section(c, x_gen, y_gen, salida)

    c.showPage()
    c.save()

    from pypdf.generic import DictionaryObject, FloatObject, NumberObject

    # ---- Label band as a self-contained Form XObject (HUELLA footprint layer) ----
    # Using FormXObject instead of merge_page() so the label's resources (PANTONE
    # colour swatches, Helvetica fonts, Nala logo spots) stay isolated inside the
    # XObject and are not merged into the page's /Resources.  At layout-generation
    # time the HUELLA layer is stripped, which physically removes /LabelFm and
    # /NalaFm from the page, eliminating their ink channels from the RIP output.
    label_buf.seek(0)
    label_reader = PdfReader(label_buf)
    label_page   = label_reader.pages[0]

    _lc = label_page[NameObject('/Contents')].get_object()
    if isinstance(_lc, ArrayObject):
        _raw_label = b'\n'.join(ref.get_object().get_data() for ref in _lc)
    else:
        _raw_label = _lc.get_data()

    _label_xobj = DecodedStreamObject()
    _label_xobj[NameObject('/Type')]     = NameObject('/XObject')
    _label_xobj[NameObject('/Subtype')]  = NameObject('/Form')
    _label_xobj[NameObject('/FormType')] = NumberObject(1)
    _label_xobj[NameObject('/BBox')] = ArrayObject([
        FloatObject(0.0), FloatObject(0.0),
        FloatObject(canvas_w), FloatObject(canvas_h),
    ])
    _lpage_res = label_page.get(NameObject('/Resources'))
    if _lpage_res is not None:
        _label_xobj[NameObject('/Resources')] = _lpage_res.clone(writer)
    _label_xobj.set_data(_raw_label)
    _label_xobj = _label_xobj.flate_encode()
    _label_fm_ref = writer._add_object(_label_xobj)

    # Register LabelFm in the page's /XObject resources so the invocation below works
    _pg_res = main_page[NameObject('/Resources')].get_object()
    if NameObject('/XObject') not in _pg_res:
        _pg_res[NameObject('/XObject')] = DictionaryObject()
    _pg_res[NameObject('/XObject')].get_object()[NameObject('/LabelFm')] = _label_fm_ref

    # ---- Crop marks FormXObject — survives strip_footprint.py (not part of HUELLA) ----
    crop_buf.seek(0)
    _crop_reader = PdfReader(crop_buf)
    _crop_page_r = _crop_reader.pages[0]
    _cc = _crop_page_r[NameObject('/Contents')].get_object()
    if isinstance(_cc, ArrayObject):
        _raw_crop = b'\n'.join(ref.get_object().get_data() for ref in _cc)
    else:
        _raw_crop = _cc.get_data()
    _crop_xobj = DecodedStreamObject()
    _crop_xobj[NameObject('/Type')]     = NameObject('/XObject')
    _crop_xobj[NameObject('/Subtype')]  = NameObject('/Form')
    _crop_xobj[NameObject('/FormType')] = NumberObject(1)
    _crop_xobj[NameObject('/BBox')] = ArrayObject([
        FloatObject(0.0), FloatObject(0.0),
        FloatObject(canvas_w), FloatObject(canvas_h),
    ])
    _crop_cpage_res = _crop_page_r.get(NameObject('/Resources'))
    if _crop_cpage_res is not None:
        _crop_xobj[NameObject('/Resources')] = _crop_cpage_res.clone(writer)
    _crop_xobj.set_data(_raw_crop)
    _crop_xobj = _crop_xobj.flate_encode()
    _crop_fm_ref = writer._add_object(_crop_xobj)
    _pg_res[NameObject('/XObject')].get_object()[NameObject('/CropFm')] = _crop_fm_ref

    # ---- Nala logo Form XObject (only when client has no logo) ----
    _has_nala = nala_h > 0
    if _has_nala:
        scale = 0.6
        nala_reader2 = PdfReader(nala_pdf_path)
        nala_page    = nala_reader2.pages[0]
        _nala_pw = float(nala_page.mediabox.width)
        _nala_ph = float(nala_page.mediabox.height)

        _nala_cont = nala_page[NameObject('/Contents')].get_object()
        if isinstance(_nala_cont, ArrayObject):
            _raw_nala = b'\n'.join(ref.get_object().get_data() for ref in _nala_cont)
        else:
            _raw_nala = _nala_cont.get_data()
        _raw_nala = re.sub(rb'/OC\s+/\w+\s+BDC\s*', b'', _raw_nala)
        _raw_nala = re.sub(rb'\bEMC\b\s*', b'', _raw_nala)

        _nala_xobj = DecodedStreamObject()
        _nala_xobj[NameObject('/Type')]     = NameObject('/XObject')
        _nala_xobj[NameObject('/Subtype')]  = NameObject('/Form')
        _nala_xobj[NameObject('/FormType')] = NumberObject(1)
        _nala_xobj[NameObject('/BBox')] = ArrayObject([
            FloatObject(0), FloatObject(0), FloatObject(_nala_pw), FloatObject(_nala_ph),
        ])
        _nala_xobj[NameObject('/Matrix')] = ArrayObject([
            FloatObject(scale), FloatObject(0), FloatObject(0), FloatObject(scale),
            FloatObject(nala_x), FloatObject(nala_y),
        ])
        _nala_res_entry = nala_page.get(NameObject('/Resources'))
        if _nala_res_entry is not None:
            _nala_xobj[NameObject('/Resources')] = _nala_res_entry.clone(writer)
        _nala_grp_entry = nala_page.get(NameObject('/Group'))
        if _nala_grp_entry is not None:
            _nala_xobj[NameObject('/Group')] = _nala_grp_entry.clone(writer)
        _nala_xobj.set_data(_raw_nala)
        _nala_xobj = _nala_xobj.flate_encode()
        _nala_xref = writer._add_object(_nala_xobj)
        _pg_res[NameObject('/XObject')].get_object()[NameObject('/NalaFm')] = _nala_xref

    # ---- Footprint invocation stream — HUELLA marked-content block ----
    # BDC/EMC marks this as Optional Content Group "HUELLA" so PDF viewers can
    # toggle the footprint layer.  strip_footprint.py removes this stream and
    # the XObject references at layout time to eliminate spurious separations.
    _fp_inv = b'/OC /HUELLA BDC\nq\n/LabelFm Do\n'
    if _has_nala:
        _fp_inv += b'/NalaFm Do\n'
    _fp_inv += b'Q\nEMC\n'
    _fp_stream = DecodedStreamObject()
    _fp_stream.set_data(_fp_inv)
    _fp_stream = _fp_stream.flate_encode()
    _fp_ref = writer._add_object(_fp_stream)

    # /Contents = [artwork_stream, footprint_stream] — two explicit streams
    main_page[NameObject('/Contents')] = ArrayObject([_new_ref, _fp_ref])

    # TrimBox = original document trim, repositioned in ET-sheet space
    _tb_x0 = offset_x - desp_x
    _tb_y0 = offset_y - desp_y
    main_page.trimbox  = RectangleObject((_tb_x0, _tb_y0, _tb_x0 + trim_w, _tb_y0 + trim_h))

    # BleedBox = TrimBox ± BLEED_ET_MM (default 5mm, editable via BLEED_ET_MM constant)
    _bl = BLEED_ET_MM * POINT_TO_MM
    main_page.bleedbox = RectangleObject((
        _tb_x0 - _bl, _tb_y0 - _bl,
        _tb_x0 + trim_w + _bl, _tb_y0 + trim_h + _bl,
    ))

    # ArtBox = TrimBox expanded by full crop-mark extent (line length = CROP_EXCESS).
    # strip_footprint.py uses this box for MediaBox/CropBox on the intermediate layout PDF.
    main_page[NameObject('/ArtBox')] = RectangleObject((
        _tb_x0 - CROP_EXCESS, _tb_y0 - CROP_EXCESS,
        _tb_x0 + trim_w + CROP_EXCESS, _tb_y0 + trim_h + CROP_EXCESS,
    ))

    # MediaBox = full ET sheet (MEDIA_EXCESS=10mm outer margin around all content)
    main_page.mediabox = RectangleObject((0.0, 0.0, float(media_w), float(media_h)))

    # CropBox = MediaBox: the full ET sheet is visible by default in PDF viewers.
    # This shows the complete approval document (artwork + crop & reg marks + label band).
    # TrimBox (prepress cut) and BleedBox (bleed area) remain separate for production use.
    main_page[NameObject('/CropBox')] = RectangleObject((0.0, 0.0, float(media_w), float(media_h)))

    # ---- Separation pages (optional — only rendered when path_images is provided) ----
    for index, image_name in enumerate(path_images or []):
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

    with open(outfile, 'wb') as f:
        writer.write(f)

    # ---- Add OCG /OCProperties via pikepdf so PDF viewers can toggle HUELLA layer ----
    _add_huella_ocg(outfile)


def _add_huella_ocg(path: str) -> None:
    """Post-process: register HUELLA OCG in catalog and page resources."""
    import tempfile, shutil
    try:
        import pikepdf as _pk
        pdf  = _pk.open(path)
        page = pdf.pages[0]

        ocg = pdf.make_indirect(_pk.Dictionary(
            Type=_pk.Name('/OCG'),
            Name=_pk.String('HUELLA'),
            Intent=_pk.Array([_pk.Name('/Design')]),
        ))
        pdf.Root['/OCProperties'] = _pk.Dictionary(
            OCGs=_pk.Array([ocg]),
            D=_pk.Dictionary(
                BaseState=_pk.Name('/ON'),
                Order=_pk.Array([ocg]),
                ON=_pk.Array([ocg]),
            ),
        )
        res = page.get('/Resources')
        if res is None:
            page['/Resources'] = _pk.Dictionary()
            res = page['/Resources']
        if '/Properties' not in res:
            res['/Properties'] = _pk.Dictionary()
        res['/Properties']['/HUELLA'] = ocg

        # Save to a temp file then replace — avoids overwriting the open file
        tmp = tempfile.mktemp(suffix='.pdf', dir=os.path.dirname(path))
        pdf.save(tmp)
        pdf.close()
        shutil.move(tmp, path)
    except Exception as _e:
        import traceback
        print(f'[one_up] OCG setup failed: {_e}')
        traceback.print_exc()


def make_all_pages(searchpath, pdffile, outfile, client, boxes_list, colorsJson, info,
                   separations_folder=None, path_images=None, names=None, logo_path=None):
    """Generate one ET sheet per source page and merge all sheets into *outfile*.

    For single-page PDFs this delegates directly to ``make()`` to avoid any
    overhead.  For multi-page PDFs each page is rendered to a temporary file
    which are then merged in order.
    """
    if len(boxes_list) == 1:
        make(searchpath, pdffile, outfile, client, boxes_list[0], colorsJson, info,
             page_index=0, separations_folder=separations_folder,
             path_images=path_images, names=names, logo_path=logo_path)
        return

    import tempfile
    from pypdf import PdfWriter as _PdfWriter

    temp_files = []
    try:
        for i, boxes in enumerate(boxes_list):
            tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
            tmp.close()
            make(searchpath, pdffile, tmp.name, client, boxes, colorsJson, info,
                 page_index=i, logo_path=logo_path)
            temp_files.append(tmp.name)

        merger = _PdfWriter()
        for tmp_path in temp_files:
            merger.append(tmp_path)
        with open(outfile, 'wb') as f:
            merger.write(f)
    finally:
        for tmp_path in temp_files:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


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
