# -*- coding: utf-8 -*-
"""
pdf_utils.py
Shared helpers for PDF reading (pypdf) and overlay compositing (ReportLab).

All mark modules follow the same pattern:
  1. Get source page dimensions with get_source_info()
  2. Create a ReportLab canvas overlay with create_overlay_canvas()
  3. Draw marks on the canvas
  4. Merge the overlay onto the source PDF with finalize_and_merge_*()
"""

import io
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas as rl_canvas


def get_source_info(pdf_path):
    """
    Return (width, height, num_pages) in PDF points for the given file.
    Reads page 0 MediaBox.
    """
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    return width, height, len(reader.pages)


def create_overlay_canvas(page_width, page_height):
    """
    Create a transparent ReportLab canvas of the given size.
    Returns (canvas, BytesIO_buffer).
    """
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(page_width, page_height))
    return c, buf


def finalize_and_merge(source_path, canvas, buf, output_path):
    """
    Save a single-page canvas and merge it on top of every page of source_path.
    canvas: ReportLab Canvas (call showPage() before passing)
    buf:    the BytesIO used when creating the canvas
    """
    canvas.save()
    buf.seek(0)
    overlay_reader = PdfReader(buf)

    source = PdfReader(source_path)
    writer = PdfWriter()

    for i, page in enumerate(source.pages):
        # Use the single overlay page for every source page
        ov_page_idx = min(i, len(overlay_reader.pages) - 1)
        page.merge_page(overlay_reader.pages[ov_page_idx])
        writer.add_page(page)

    with open(output_path, 'wb') as f:
        writer.write(f)


def finalize_and_merge_multipage(source_path, pages_canvases, output_path):
    """
    Merge per-page overlays onto a source PDF.
    pages_canvases: list of (Canvas, BytesIO) — one entry per source page.
                    Each canvas must have showPage() already called.
    """
    source = PdfReader(source_path)
    writer = PdfWriter()

    overlay_readers = []
    for cv, buf in pages_canvases:
        cv.save()
        buf.seek(0)
        overlay_readers.append(PdfReader(buf))

    for i, page in enumerate(source.pages):
        if i < len(overlay_readers):
            page.merge_page(overlay_readers[i].pages[0])
        writer.add_page(page)

    with open(output_path, 'wb') as f:
        writer.write(f)


def create_enlarged_page(source_path, target_width, target_height,
                          offset_x, offset_y, output_path,
                          extra_pages_canvases=None):
    """
    Create an output PDF where each source page is placed on a larger canvas
    at (offset_x, offset_y).  Useful for one_up which adds a label margin.

    extra_pages_canvases: optional list of (Canvas, BytesIO) for extra pages
                          appended after the main page.
    """
    source = PdfReader(source_path)
    writer = PdfWriter()

    for src_page in source.pages:
        new_page = writer.add_blank_page(target_width, target_height)
        new_page.merge_transformed_page(
            src_page,
            Transformation().translate(tx=offset_x, ty=offset_y),
        )

    if extra_pages_canvases:
        for cv, buf in extra_pages_canvases:
            cv.save()
            buf.seek(0)
            extra_reader = PdfReader(buf)
            for ep in extra_reader.pages:
                writer.add_page(ep)

    with open(output_path, 'wb') as f:
        writer.write(f)
