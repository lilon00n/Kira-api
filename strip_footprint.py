# -*- coding: utf-8 -*-
"""
strip_footprint.py
Strips the HUELLA footprint layer from a OneUP ET-sheet PDF.

OneUP PDFs carry a two-stream /Contents:
  [0]  artwork_stream  — customer artwork (q/cm/Q block, no footprint inks)
  [1]  footprint_stream — label band + Nala logo invocation (BDC/EMC wrapped)

At layout-generation time this module:
  1. Drops the footprint content stream (index >= 1).
  2. Removes /LabelFm and /NalaFm from page /XObject resources.
  3. Removes /HUELLA from page /Properties.
  4. Removes /OCProperties from the catalog.
  5. Resizes MediaBox and CropBox to match BleedBox.
     TrimBox and BleedBox are left untouched (used by layout calculations).

Result: a compact PDF containing only the artwork ink channels — no colour-bar
swatches, no Nala-logo spots, no footprint /Separation colorspaces — so the
RIP/GS output separations match the original document exactly.
"""

import pikepdf


def strip_huella(src_path: str, dst_path: str) -> None:
    """Strip HUELLA footprint layer from *src_path* and save to *dst_path*."""
    pdf  = pikepdf.open(src_path)
    page = pdf.pages[0]

    # 1. Keep only the first /Contents stream (artwork)
    contents = page.get('/Contents')
    if contents is not None:
        if isinstance(contents, pikepdf.Array) and len(contents) > 1:
            page['/Contents'] = pikepdf.Array([contents[0]])
        # Single-stream file (old format without HUELLA): nothing to trim

    # 2. Remove footprint XObjects from page resources
    res = page.get('/Resources')
    if res is not None:
        xobj = res.get('/XObject')
        if xobj is not None:
            for key in ('/LabelFm', '/NalaFm'):
                if key in xobj:
                    del xobj[key]
        props = res.get('/Properties')
        if props is not None and '/HUELLA' in props:
            del props['/HUELLA']

    # 3. Resize MediaBox and CropBox to BleedBox (separate array instances)
    bleedbox = page.get('/BleedBox')
    if bleedbox is not None:
        bb_vals = [v for v in bleedbox]
        page['/MediaBox'] = pikepdf.Array(bb_vals)
        page['/CropBox']  = pikepdf.Array(bb_vals)
        # TrimBox and BleedBox stay at their original coordinates

    # 4. Remove /OCProperties from catalog
    root = pdf.Root
    if '/OCProperties' in root:
        del root['/OCProperties']

    pdf.save(dst_path)
