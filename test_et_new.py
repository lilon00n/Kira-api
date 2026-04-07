# -*- coding: utf-8 -*-
"""
test_et_new.py
===================================
Genera hojas ET + marcas para los 3 nuevos archivos de prueba:
  - 1circular_etiq.ai
  - APOLO aveztruz_3.ai
  - APOLO aveztruz_4.ai

Los colores se leen automáticamente del archivo de entrada.
La geometría (trim/bleed) se lee de los PDF boxes.

Genera en output/:
  ET_circular_oneup.pdf / ET_circular_marcas.pdf
  ET_apolo3_oneup.pdf   / ET_apolo3_marcas.pdf
  ET_apolo4_oneup.pdf   / ET_apolo4_marcas.pdf

Uso:
  cd C:\\Users\\lilo\\Documents\\Fundacion\\Nala\\kira-api
  .\\venv-new\\Scripts\\python.exe test_et_new.py
"""

import json, os, sys, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.makedirs(os.path.join(BASE, 'output'), exist_ok=True)

from pypdf import PdfReader
from read_spots import extract_spots_from_pdf
from ink_coverage import calculate_coverage

# ------------------------------------------------------------------
# Trabajos a procesar
# ------------------------------------------------------------------
JOBS = [
    {
        'label':    'Etiqueta Circular',
        'source':   os.path.join(BASE, 'input', '1circular_etiq.ai'),
        'out_et':   os.path.join(BASE, 'output', 'ET_circular_oneup.pdf'),
        'out_mrk':  os.path.join(BASE, 'output', 'ET_circular_marcas.pdf'),
        'info': {
            'customer':      'Cliente Demo',
            'salesman':      'Vendedor Demo',
            'tsCode':        'TS-2026-CIRC',
            'fileName':      '1circular_etiq.ai',
            'productType':   'Etiqueta circular',
            'barcodeType':   '',
            'barcodeNumber': '',
            'designer':      '',
            'materialMachines': [{'machine': 'Demo', 'material': 'PP Blanco'}],
            'salida': '',
        },
    },
    {
        'label':    'APOLO Avestruz 3',
        'source':   os.path.join(BASE, 'input', 'APOLO aveztruz_3.ai'),
        'out_et':   os.path.join(BASE, 'output', 'ET_apolo3_oneup.pdf'),
        'out_mrk':  os.path.join(BASE, 'output', 'ET_apolo3_marcas.pdf'),
        'info': {
            'customer':      'APOLO',
            'salesman':      'Vendedor Demo',
            'tsCode':        'TS-2026-APO3',
            'fileName':      'APOLO aveztruz_3.ai',
            'productType':   'Etiqueta APOLO Avestruz',
            'barcodeType':   '',
            'barcodeNumber': '',
            'designer':      '',
            'materialMachines': [{'machine': 'Demo', 'material': 'PP Blanco'}],
            'salida': '',
        },
    },
    {
        'label':    'APOLO Avestruz 4',
        'source':   os.path.join(BASE, 'input', 'APOLO aveztruz_4.ai'),
        'out_et':   os.path.join(BASE, 'output', 'ET_apolo4_oneup.pdf'),
        'out_mrk':  os.path.join(BASE, 'output', 'ET_apolo4_marcas.pdf'),
        'info': {
            'customer':      'APOLO',
            'salesman':      'Vendedor Demo',
            'tsCode':        'TS-2026-APO4',
            'fileName':      'APOLO aveztruz_4.ai',
            'productType':   'Etiqueta APOLO Avestruz',
            'barcodeType':   '',
            'barcodeNumber': '',
            'designer':      '',
            'materialMachines': [{'machine': 'Demo', 'material': 'PP Blanco'}],
            'salida': '',
        },
    },
]

MARK_SIZE   = 8    # mm
MARK_WEIGHT = 0.5  # pt
MARK_DIST   = 3    # mm


def process_job(job):
    label  = job['label']
    source = job['source']

    print('=' * 60)
    print(f'Trabajo: {label}')
    print(f'Archivo: {os.path.basename(source)}')

    if not os.path.exists(source):
        print(f'  !! ARCHIVO NO ENCONTRADO: {source}')
        return

    # ---- Leer geometría ----------------------------------------
    reader   = PdfReader(source)
    page     = reader.pages[0]
    media_w  = float(page.mediabox.width)
    media_h  = float(page.mediabox.height)
    tb = page.trimbox  or page.mediabox
    bb = page.bleedbox or page.mediabox

    trim_w_pt  = float(tb.right)  - float(tb.left)
    trim_h_pt  = float(tb.top)    - float(tb.bottom)
    trim_w_mm  = trim_w_pt / 2.835
    trim_h_mm  = trim_h_pt / 2.835
    bleed_mm   = round((float(tb.left) - float(bb.left)) / 2.835, 1)

    BOXES = {
        'bleed':      [float(bb.left), float(bb.bottom)],
        'trim':       [float(tb.left), float(tb.bottom)],
        'trimWidth':  str(round(trim_w_mm, 3)),
        'trimHeight': str(round(trim_h_mm, 3)),
    }

    print(f'Página:  {round(media_w/2.835,1)} x {round(media_h/2.835,1)} mm')
    print(f'Trim:    {round(trim_w_mm,1)} x {round(trim_h_mm,1)} mm')
    print(f'Bleed:   {bleed_mm} mm por lado')

    # ---- Leer colores spot del archivo -------------------------
    colors = extract_spots_from_pdf(source)
    # Calcular cobertura de tinta real por canal usando Ghostscript
    print(f'Calculando cobertura de tinta...')
    coverage = calculate_coverage(source, [c['name'] for c in colors])
    for c in colors:
        c['inkCov'] = coverage.get(c['name'], '0')
    print(f'Colores: {", ".join(c["name"] + " " + c["inkCov"] + "%" for c in colors)}')

    # ---- PARTE 1: one_up ---------------------------------------
    print(f'\n[ET]  Generando hoja ET...')
    from one_up import make as make_one_up
    make_one_up(
        BASE,
        source,
        job['out_et'],
        'default',
        json.dumps(BOXES),
        colors,
        json.dumps(job['info']),
        os.path.join(BASE, 'input') + os.sep,
        [],
        [],
    )
    print(f'   ✓  {os.path.basename(job["out_et"])}  ({os.path.getsize(job["out_et"])//1024} KB)')

    # ---- PARTE 2: marcas ---------------------------------------
    print(f'[MRK] Aplicando marcas...')
    out_mrk = job['out_mrk']
    dist    = MARK_DIST * 2.835

    x_margin          = float(tb.left)
    y_margin_from_top = media_h - float(tb.top)
    w_trim            = trim_w_pt
    h_trim            = trim_h_pt

    # Crop marks
    from crop_mark import make as mk_crop
    mk_crop(
        BASE, source, out_mrk,
        colors,
        x_margin, y_margin_from_top,
        MARK_SIZE * 2.835, w_trim, h_trim,
        dist, dist, MARK_WEIGHT,
    )

    tmp = os.path.join(BASE, 'output', '_tmp.pdf')

    # Registration marks
    from registration_mark import make as mk_reg
    cx      = float(tb.left) + w_trim / 2
    cy_top  = media_h - float(tb.top)    - dist - 8
    cy_bot  = media_h - float(tb.bottom) + dist + 8
    mk_reg(BASE, out_mrk, tmp, colors, cx, cy_top, 5, MARK_WEIGHT)
    shutil.move(tmp, out_mrk)
    mk_reg(BASE, out_mrk, tmp, colors, cx, cy_bot, 5, MARK_WEIGHT)
    shutil.move(tmp, out_mrk)

    # Color names
    from color_names import make as mk_cnames
    x_names = float(tb.left)  - dist - 2
    y_names = media_h - float(tb.bottom) - h_trim / 2
    mk_cnames(BASE, out_mrk, tmp, colors, 7, x_names, y_names, 'L', 'f', 'i')
    shutil.move(tmp, out_mrk)

    # Colors bar
    from colors_bar import make as mk_cbar
    x_bar = float(tb.right) + dist
    y_bar = media_h - float(tb.bottom)
    mk_cbar(BASE, out_mrk, tmp, colors, '1,0.7,0.5,0.2', 10,
            x_bar, y_bar, 'L', 'f', 'f')
    shutil.move(tmp, out_mrk)

    print(f'   ✓  {os.path.basename(out_mrk)}  ({os.path.getsize(out_mrk)//1024} KB)')


# ------------------------------------------------------------------
# Verificar colores en salida con pypdf
# ------------------------------------------------------------------
def verify_separations(filepath):
    from pypdf import PdfReader
    reader = PdfReader(filepath)
    page   = reader.pages[0]
    res    = page.get("/Resources", {})
    cs     = res.get("/ColorSpace", {})
    print(f'\n  Separaciones en {os.path.basename(filepath)}:')
    for k in cs.keys():
        try:
            arr = list(cs[k])
            cs_type = str(arr[0]) if arr else "?"
            cs_name = str(arr[1]).lstrip("/") if len(arr) > 1 else "?"
            print(f'    {cs_name:30s} → {cs_type}')
        except Exception:
            pass


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
for job in JOBS:
    process_job(job)

print('\n' + '=' * 60)
print('Verificando colores en PDFs generados...')
for job in JOBS:
    if os.path.exists(job['out_et']):
        verify_separations(job['out_et'])

print('\n' + '=' * 60)
print('Archivos generados en output/:')
for job in JOBS:
    for f in [job['out_et'], job['out_mrk']]:
        if os.path.exists(f):
            print(f'  {os.path.basename(f):35s}  {os.path.getsize(f)//1024} KB')

print()
