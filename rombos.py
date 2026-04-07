# -*- coding: utf-8 -*-
"""
rombos.py
Places a second PDF (rombofile) at coordinates (x, y) on top of the source PDF.
Migrated from PDFlib to reportlab + pypdf.

Note: the original uses topdown=true, so y is measured from the top.
With pypdf merge_transformed_page we use bottom-up coordinates (PDF standard).
"""

import os
import io
from pypdf import PdfReader, PdfWriter, Transformation
from pdf_utils import get_source_info


def make(searchpath, pdffile, outfile, rombofile, x, y):
    x = float(x)
    y = float(y)

    page_width, page_height, num_pages = get_source_info(pdffile)

    # Convert top-down y to bottom-up
    place_y = page_height - y

    source = PdfReader(pdffile)
    rombo_reader = PdfReader(rombofile)
    rombo_page = rombo_reader.pages[0]

    writer = PdfWriter()
    for src_page in source.pages:
        # Merge rombo at (x, place_y) on top of source
        src_page.merge_transformed_page(
            rombo_page,
            Transformation().translate(tx=x, ty=place_y),
        )
        writer.add_page(src_page)

    with open(outfile, 'wb') as f:
        writer.write(f)
