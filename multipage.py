# -*- coding: utf-8 -*-
"""
multipage.py
Opens a source PDF, copies its first page, then appends one extra page per
separation TIFF image with the image and a colour-name label.
Migrated from PDFlib to reportlab + pypdf + Pillow.
"""

import io
import os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import black


def make(searchpath, pdffile, outfile, separationsFolder, pathImages, names):
    source = PdfReader(pdffile)
    page_width  = float(source.pages[0].mediabox.width)
    page_height = float(source.pages[0].mediabox.height)

    writer = PdfWriter()

    # Copy first page of source as-is
    writer.add_page(source.pages[0])

    # One page per separation TIFF
    for index, image_name in enumerate(pathImages):
        img_path = separationsFolder + image_name
        sep_height = page_height + 10  # extra 10 pt for the label row at bottom

        buf = io.BytesIO()
        c = Canvas(buf, pagesize=(page_width, sep_height))

        # Draw the TIFF image (Pillow handles reading via ReportLab's drawImage)
        c.drawImage(img_path, 0, 10, width=page_width, height=page_height,
                    preserveAspectRatio=True)

        # Colour name label at the very bottom
        c.setFont('Helvetica', 10)
        c.setFillColor(black)
        c.drawString(0, 0, names[index])

        c.showPage()
        c.save()
        buf.seek(0)

        sep_reader = PdfReader(buf)
        writer.add_page(sep_reader.pages[0])
        print(image_name)

    with open(outfile, 'wb') as f:
        writer.write(f)
