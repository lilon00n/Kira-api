# -*- coding: utf-8 -*-
"""
api.py
Flask API for Kira PDF processing.
Migrated from PDFlib to reportlab + pypdf.
"""

import json
import os
import traceback

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('ENV', 'production') == 'development'

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bad_request(msg: str):
    return jsonify({'error': msg}), 400


def _server_error(exc: Exception):
    traceback.print_exc()
    return jsonify({'error': str(exc)}), 500


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def home():
    return '<h1>Kira API</h1><p>PDF processing service is running.</p>'


# ---------------------------------------------------------------------------
# Mark routes
# ---------------------------------------------------------------------------

@app.route('/supportBar', methods=['POST'])
def supportBar():
    try:
        from support_bar import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['x'], body['y'],
            body['width'], body['height'], body['percent'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/colorNames', methods=['POST'])
def colorNames():
    try:
        from color_names import make
        body = request.get_json(force=True)
        ret = make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['fsize'], body['x'], body['y'],
            body['place'], body['sideX'], body['sideY'],
        )
        return ret
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/strip-footprint', methods=['POST'])
def strip_footprint_route():
    try:
        from strip_footprint import strip_huella
        body = request.get_json(force=True)
        src  = body['src']
        dst  = body['dst']
        strip_huella(src, dst)
        return jsonify({'ok': True, 'dst': dst})
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/colorsBar', methods=['POST'])
def colorsBar():
    try:
        from colors_bar import make
        body = request.get_json(force=True)
        ret = make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['intensities'], body['size'],
            body['x'], body['y'], body['place'], body['sideX'], body['sideY'],
        )
        return ret
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/cropMark', methods=['POST'])
def cropMark():
    try:
        from crop_mark import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['x_margin'], body['y_margin'],
            body['size'], body['width'], body['height'],
            body['dist_width'], body['dist_height'], body['weight'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/cropStations', methods=['POST'])
def cropStations():
    try:
        from crop_stations import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['stationsMarks'], body['size'],
            body['dist_width'], body['dist_height'], body['weight'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/registrationMark', methods=['POST'])
def registrationMark():
    try:
        from registration_mark import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['x'], body['y'],
            body['crop_size'], body['weight'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/info', methods=['POST'])
def info():
    try:
        from info import make
        body = request.get_json(force=True)
        ret = make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['info'], body['fsize'],
            body['x'], body['y'], body['place'],
            body['sideX'], body['sideY'],
        )
        return ret
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/impositionInfo', methods=['POST'])
def impositionInfo():
    try:
        from imposition_info import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'],
            body['sheetNum'], body['sheetTotal'], body['side'],
            body['sheetWidth'], body['sheetHeight'],
            body['qtyWidth'], body['qtyHeight'],
            body['gapWidth'], body['gapHeight'],
            body['pinzaPapel'], body['colaMargen'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/micropoint', methods=['POST'])
def micropoint():
    try:
        from micropoint import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['x'], body['y'], body['size'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/rombos', methods=['POST'])
def rombos():
    try:
        from rombos import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['rombofile'], body['x'], body['y'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/circles', methods=['POST'])
def circles():
    try:
        from circles import make
        body = request.get_json(force=True)
        ret = make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['x'], body['y'], body['colors'],
            body['place'], body['sideX'], body['sideY'],
        )
        return ret
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/oneUp', methods=['POST'])
def makeOneUp():
    try:
        body = request.get_json(force=True)
        boxes = body['boxes']
        if isinstance(boxes, list):
            # Multi-page: boxes is an array of per-page box dicts
            from one_up import make_all_pages
            make_all_pages(
                body['searchpath'],
                body['pdffile'],
                body['outfile'],
                body['client'],
                boxes,
                body['colors'],
                json.dumps(body['info']),
                body.get('separationsFolder', ''),
                body.get('pathImages', []),
                body.get('names', []),
                logo_path=body.get('logoPath', ''),
            )
        else:
            # Single-page (backward compatible)
            from one_up import make
            make(
                body['searchpath'],
                body['pdffile'],
                body['outfile'],
                body['client'],
                json.dumps(boxes),
                body['colors'],
                json.dumps(body['info']),
                separations_folder=body.get('separationsFolder', ''),
                path_images=body.get('pathImages', []),
                names=body.get('names', []),
                logo_path=body.get('logoPath', ''),
            )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/multipage', methods=['POST'])
def makeMultipage():
    try:
        from multipage import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['separationsFolder'], body['pathImages'], body['names'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/inkCoverage', methods=['POST'])
def getInkCoverage():
    try:
        import numpy as np
        from PIL import Image as PILImage
        body  = request.get_json(force=True)
        paths = [p.strip() for p in body['paths'].split(',') if p.strip()]
        result = []
        for p in paths:
            try:
                im  = PILImage.open(p).convert("L")
                arr = np.array(im, dtype=np.float32)
                # tiffsep: 0 = full ink, 255 = no ink  → coverage = 1 - mean/255
                result.append(1.0 - float(arr.mean() / 255.0))
            except Exception:
                result.append(0.0)
        return jsonify(result)
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


# ---------------------------------------------------------------------------
# TrimBox from separation
# ---------------------------------------------------------------------------

@app.route('/getSeparationNames', methods=['POST'])
def getSeparationNames():
    try:
        from set_trimbox import get_separation_names
        body = request.get_json(force=True)
        pdf_path = body['pdffile']
        names = get_separation_names(pdf_path)
        return jsonify({'ok': True, 'separations': names})
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/classifySeparations', methods=['POST'])
def classifySeparations():
    """Classify a list of separation names into ink categories.
    Body: { "names": ["Die Cut", "White", "CMYK C", ...] }
    Returns: { "ok": true, "classifications": [{name, category, label, is_die_cut}, ...] }
    """
    try:
        from set_trimbox import classify_separation
        body = request.get_json(force=True)
        names = body.get('names', [])
        if not isinstance(names, list):
            return _bad_request('names must be an array')
        result = [dict(name=n, **classify_separation(n)) for n in names]
        return jsonify({'ok': True, 'classifications': result})
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/extractInks', methods=['POST'])
def extractInks():
    """
    Detect process and spot inks from a PDF.
    Body: { "pdffile": "/abs/path/file.pdf" }
    Returns: { ok, process, processDetected, spots }
    """
    try:
        from services.pdf_inks import extract_inks
        body = request.get_json(force=True)
        result = extract_inks(body['pdffile'])
        return jsonify({'ok': True, **result})
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/renderChannels', methods=['POST'])
def renderChannels():
    """
    Render a PDF with selected process/spot channels enabled.
    Body:
      {
        "pdffile": "/abs/path/file.pdf",
        "channels": {"cyan": true, "magenta": true, "yellow": true, "black": true},
        "spots": {"PANTONE 485 C": true}
      }
    Returns: { ok, pdfBase64 }
    """
    try:
        from services.pdf_inks import render_channels
        body = request.get_json(force=True)
        result = render_channels(
            body['pdffile'],
            body.get('channels', {}),
            body.get('spots', {}),
        )
        return jsonify(result)
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/convertRgbToCmykSelective', methods=['POST'])
def convertRgbToCmykSelective():
        """
        Convert only RGB objects to CMYK while preserving DeviceN/Spot/CMYK and pure black vectors/text.
        Body:
            {
                "pdffile": "/abs/path/source.pdf",
                "outfile": "/abs/path/output.pdf",
                "iccProfile": "/abs/path/profile.icc"
            }
        """
        try:
            from services.pdf_inks import convert_rgb_to_cmyk_selective
            body = request.get_json(force=True)
            result = convert_rgb_to_cmyk_selective(
                    body['pdffile'],
                    body['outfile'],
                    body.get('iccProfile'),
            )
            return jsonify({'ok': True, **result})
        except (KeyError, TypeError) as e:
            return _bad_request(str(e))
        except Exception as e:
            return _server_error(e)


@app.route('/injectColourText', methods=['POST'])
def injectColourText():
    """Inject a named spot-colour swatch into an existing PDF (in place).
    Body: { "pdffile": "/abs/path/file.pdf", "colourName": "Special Blue", "r": 0, "g": 100, "b": 200 }
    Returns: { "ok": true } or { "ok": false, "error": "..." }
    """
    try:
        from inject_colour_text import inject_colour_text
        body = request.get_json(force=True)
        result = inject_colour_text(
            body['pdffile'],
            body['colourName'],
            int(body.get('r', 0)),
            int(body.get('g', 0)),
            int(body.get('b', 0)),
            c=body.get('c'),   # 0-100 from Nala DB, optional
            m=body.get('m'),
            y=body.get('y'),
            k=body.get('k'),
        )
        if result['ok']:
            return jsonify(result)
        return jsonify(result), 422
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/setTrimboxFromSeparation', methods=['POST'])
def setTrimboxFromSeparation():
    try:
        from set_trimbox import set_trimbox_from_separation
        body = request.get_json(force=True)
        result = set_trimbox_from_separation(
            body['pdffile'],
            body['outfile'],
            body.get('separationName'),   # None → auto-detect
        )
        if result['ok']:
            return jsonify(result)
        return jsonify(result), 422
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/flattenPdf', methods=['POST'])
def flattenPdf():
    """
    Convert a PDF to compatibility level 1.3 using GhostScript (pdfwrite).
    Resolves font/version issues with legacy RIPs (Harlequin etc.).
    Body: {
      pdfPath:      absolute path to the source PDF,
      outputPath:   (optional) destination path — overwrites source if omitted,
      compatLevel:  (optional) float, default 1.3,
      outlineFonts: (optional) bool, default true — convert text to curves
    }
    """
    try:
        import subprocess, shutil, os
        from set_trimbox import _find_gs

        body         = request.get_json(force=True)
        pdf_path     = body.get('pdfPath')
        output_path  = body.get('outputPath') or pdf_path
        compat       = str(body.get('compatLevel', 1.3))
        outline_fonts = body.get('outlineFonts', True)

        if not pdf_path:
            return _bad_request('pdfPath is required')
        if not os.path.isfile(pdf_path):
            return _bad_request(f'File not found: {pdf_path}')

        gs = _find_gs()

        # Write to a temp file first so we never corrupt the source
        tmp = pdf_path + '.tmp_flatten.pdf'
        cmd = [
            gs,
            '-dBATCH', '-dNOPAUSE', '-dQUIET',
            '-sDEVICE=pdfwrite',
            f'-dCompatibilityLevel={compat}',
            f'-sOutputFile={tmp}',
            pdf_path,
        ]
        if outline_fonts:
            cmd.insert(-1, '-dNoOutputFonts')

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            if os.path.exists(tmp):
                os.remove(tmp)
            return jsonify({'ok': False, 'error': result.stderr[:500]}), 500

        shutil.move(tmp, output_path)
        size = os.path.getsize(output_path)
        return jsonify({'ok': True, 'outputPath': output_path, 'sizeBytes': size})

    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/injectHalftone', methods=['POST'])
def injectHalftone():
    """
    Inject a PDF Type 5 Halftone dictionary into a PDF file.
    Body: {
      pdfPath:      absolute path to the PDF (overwritten in place if outputPath omitted),
      screeningSet: { default: [shape,freq,angle,"",""], exceptions: [{ColorName:[...]},...] },
      outputPath:   (optional) write to a different file instead of overwriting
    }
    """
    try:
        body = request.get_json(force=True)
        pdf_path      = body.get('pdfPath')
        screening_set = body.get('screeningSet')
        output_path   = body.get('outputPath')   # optional
        if not pdf_path or not screening_set:
            return _bad_request('pdfPath and screeningSet are required')
        from inject_halftone import inject_halftone
        result = inject_halftone(pdf_path, screening_set, output_path)
        if result['ok']:
            return jsonify(result)
        return jsonify(result), 500
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/embed-screening', methods=['POST'])
def embedScreening():
    """
    Inject a PDF Type 5 Halftone into a PDF using pikepdf (no re-distillation).
    Accepts Nala's per-separation format directly.
    Body: {
      pdfPath:     absolute path to source PDF,
      outputPath:  (optional) destination path — overwrites source if omitted,
      separations: [{name, angle, frequency, psName}, ...]
    }
    psName is the Harlequin/PDF spot-function name (e.g. "SimpleDot", "Round").
    """
    try:
        import re
        body        = request.get_json(force=True)
        pdf_path    = body.get('pdfPath')
        output_path = body.get('outputPath')
        separations = body.get('separations', [])
        if not pdf_path or not separations:
            return _bad_request('pdfPath and separations are required')

        # Use Black (or first) separation as /Default
        black_sep = next(
            (s for s in separations if re.search(r'black|negro|\bk\b|key', s.get('name', ''), re.I)),
            separations[0]
        )
        screening_set = {
            'default': [
                black_sep.get('psName') or 'SimpleDot',
                float(black_sep['frequency']),
                float(black_sep['angle']),
                '', '',
            ],
            'exceptions': [
                {s['name']: [s.get('psName') or 'SimpleDot', float(s['frequency']), float(s['angle']), '', '']}
                for s in separations
            ],
        }

        from inject_halftone import inject_halftone
        result = inject_halftone(pdf_path, screening_set, output_path)
        if result['ok']:
            return jsonify(result)
        return jsonify(result), 500
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


# ---------------------------------------------------------------------------
# Preflight routes
# ---------------------------------------------------------------------------

@app.route('/preflight/analyze', methods=['POST'])
def preflightAnalyze():
    """
    Analyze a PDF for preflight issues.
    Body: { pdfPath, maxDpi (optional, default 300) }
    Returns: { ok, issues, hasIssues, rgbContent, whiteOverprint, enrichedBlack, imageResolution, fonts, spots }
    """
    try:
        from preflight import analyze_pdf
        body     = request.get_json(force=True)
        pdf_path = body.get('pdfPath')
        max_dpi  = float(body.get('maxDpi', 300))
        if not pdf_path:
            return _bad_request('pdfPath is required')
        result = analyze_pdf(pdf_path, max_dpi)
        return jsonify(result)
    except FileNotFoundError as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/preflight/fix', methods=['POST'])
def preflightFix():
    """
    Apply preflight fixes to a PDF and save result to outPath.
    Body: {
      pdfPath,
      outPath,
      iccProfile (optional, default "fogra39"),
      options: {
        convertRgb (bool, default true),
        outlineFonts (bool, default false),
        downsampleImages (bool, default false),
        maxDpi (number, default 300)
      }
    }
    Returns: { ok, outPath, appliedFixes, fixCount }
    """
    try:
        from preflight import fix_pdf
        body       = request.get_json(force=True)
        pdf_path   = body.get('pdfPath')
        out_path   = body.get('outPath')
        options    = body.get('options', {})
        icc        = body.get('iccProfile', 'fogra39')
        if not pdf_path or not out_path:
            return _bad_request('pdfPath and outPath are required')
        result = fix_pdf(pdf_path, out_path, options, icc)
        return jsonify(result)
    except FileNotFoundError as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


# ---------------------------------------------------------------------------
# Imposition routes
# ---------------------------------------------------------------------------

@app.route('/imposeSchemes', methods=['GET'])
def imposeSchemes():
    """Return the list of supported imposition schemes."""
    return jsonify({'schemes': ['saddle']})


@app.route('/impose', methods=['POST'])
def impose():
    """
    Impose a PDF as a printed booklet.
    Body: {
      pdffile   : absolute path to source PDF (reader order),
      outfile   : absolute path for output imposed PDF,
      scheme    : (optional) "saddle" (default),
      marginMm  : (optional) outer margin in mm (default 10),
      bleedMm   : (optional) bleed already in source PDF in mm (default 3),
      marks     : (optional) bool, add prepress marks (default true),
      colors    : (optional) [{name, l, a, ba}, ...] for colour bar
    }
    Returns: { ok: true, pages, padded_pages, sheets }
    """
    try:
        from imposition import make_saddle
        body   = request.get_json(force=True)
        scheme = body.get('scheme', 'saddle')
        if scheme != 'saddle':
            return _bad_request(f'Unknown scheme: {scheme}. Supported: saddle')
        result = make_saddle(
            pdffile   = body['pdffile'],
            outfile   = body['outfile'],
            margin_mm = float(body.get('marginMm', 10)),
            bleed_mm  = float(body.get('bleedMm', 3)),
            colors    = body.get('colors', []),
            marks     = bool(body.get('marks', True)),
        )
        return jsonify({'ok': True, **result})
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


# ---------------------------------------------------------------------------
# Offset imposition
# ---------------------------------------------------------------------------

@app.route('/offsetImpose', methods=['POST'])
def makeOffsetImposition():
    """
    Pipeline: imposición → marcas de corte → info del pliego.

    Body JSON:
      pdffile           : ruta del PDF fuente de la etiqueta
      outfile           : ruta del PDF final de salida
      searchpath        : carpeta de recursos (PDFlib compat, puede ser ".")
      colors            : array de tintas spot para las marcas
      plateWidth        : ancho plancha mm (MediaBox)
      plateHeight       : alto plancha mm
      paperWidth        : ancho papel mm (CropBox)
      paperHeight       : alto papel mm
      qtyWidth          : columnas
      qtyHeight         : filas
      gapWidth          : gap horizontal mm
      gapHeight         : gap vertical mm
      marginWidth       : margen lateral mm (actualmente ignorado — centrado automático)
      pinzaPlancha      : pinza plancha mm (def. 47)
      pinzaPapel        : pinza papel mm (def. 13)
      colaMargen        : cola / control strip mm (def. 6)
      cropSize          : longitud de las marcas de corte mm (def. 3)
      cropDist          : distancia marca-borde grilla mm (def. 2)
      cropWeight        : grosor líneas de corte pt (def. 0.25)
      sheetNum          : número de este pliego (def. 1)
      sheetTotal        : total pliegos del trabajo (def. 1)
      side              : 'Frente' o 'Dorso' (def. 'Frente')
    """
    import os, tempfile
    try:
        from offset_impose import make_offset_imposition
        from crop_stations  import make as make_crop
        from imposition_info import make as make_info

        body = request.get_json(force=True)

        pdffile      = body['pdffile']
        pdffile_back = body.get('pdffile_back', None)
        outfile    = body['outfile']
        searchpath = body.get('searchpath', '.')
        colors     = body.get('colors', [{'name': 'All', 'book': '', 'density': 1}])

        plate_w    = float(body['plateWidth'])
        plate_h    = float(body['plateHeight'])
        paper_w    = float(body['paperWidth'])
        paper_h    = float(body['paperHeight'])
        qty_w      = int(body['qtyWidth'])
        qty_h      = int(body['qtyHeight'])
        gap_w      = float(body['gapWidth'])
        gap_h      = float(body['gapHeight'])
        margin_w   = float(body.get('marginWidth', 0))
        pinza_p    = float(body.get('pinzaPlancha', 47))
        pinza_pap  = float(body.get('pinzaPapel',   13))
        cola       = float(body.get('colaMargen',    6))
        mode       = body.get('mode', 'simplex')

        crop_size   = float(body.get('cropSize',   3))
        crop_dist   = float(body.get('cropDist',   2))
        crop_weight = float(body.get('cropWeight', 0.25))

        sheet_num   = int(body.get('sheetNum',   1))
        sheet_total = int(body.get('sheetTotal', 1))
        side        = body.get('side', 'Frente')

        # ── Paso 1: imposición ─────────────────────────────────────────────
        tmp1 = outfile + '.step1.pdf'
        result = make_offset_imposition(
            pdffile          = pdffile,
            pdffile_back     = pdffile_back,
            outfile          = tmp1,
            plate_w_mm       = plate_w,
            plate_h_mm       = plate_h,
            paper_w_mm       = paper_w,
            paper_h_mm       = paper_h,
            qty_w            = qty_w,
            qty_h            = qty_h,
            gap_w_mm         = gap_w,
            gap_h_mm         = gap_h,
            margin_w_mm      = margin_w,
            pinza_plancha_mm = pinza_p,
            pinza_papel_mm   = pinza_pap,
            cola_margen_mm   = cola,
            mode             = mode,
        )

        # ── Paso 2: marcas de corte ────────────────────────────────────────
        # make_offset_imposition() ya calculó las stations en formato
        # correcto para crop_stations (mm, yStart top-down desde el borde
        # superior del PDF). Para W&T y H2H hay 2 stations (frente + reverso).
        tmp2 = outfile + '.step2.pdf'
        make_crop(
            searchpath, tmp1, tmp2,
            colors,
            result['stations'],
            crop_size, crop_dist, crop_dist, crop_weight,
        )

        # ── Paso 3: texto informativo en la zona de cola ───────────────────
        make_info(
            searchpath, tmp2, outfile,
            colors,
            sheet_num, sheet_total, side,
            paper_w, paper_h,
            qty_w, qty_h,
            gap_w, gap_h,
            pinza_pap, cola,
        )

        # limpiar temporales
        for f in (tmp1, tmp2):
            try: os.remove(f)
            except OSError: pass

        return jsonify({'ok': True, **result})
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


# ---------------------------------------------------------------------------
# Mechanics routes
# ---------------------------------------------------------------------------

@app.route('/mechanics/generate', methods=['POST'])
def mechanicsGenerate():
    """
    Generate a parametric mechanical packaging template as a vector PDF.

    Body: {
      family:     string  — 'pillow_bag' | 'gusseted_bag' | 'sleeve'
      params:     object  — family-specific parameters (all dimensions in mm)
      outputPath: string  — absolute path for the output PDF
    }

    Pillow bag params: width, repeat, seal_top, seal_bottom, fin_overlap
    Gusseted bag params: width, repeat, seal_top, seal_bottom, gusset_depth
    Sleeve params: width, repeat, overlap

    Optional params (all families): bleed, safe_inset, artwork_inset

    Returns: { ok: true, family, outputPath } or { error: '...' }
    """
    try:
        from mechanics.families import get_generator
        from mechanics.renderer import PDFRenderer

        body        = request.get_json(force=True)
        family      = body.get('family')
        params      = body.get('params')
        output_path = body.get('outputPath')

        if not family:
            return _bad_request("'family' is required")
        if not params:
            return _bad_request("'params' is required")
        if not output_path:
            return _bad_request("'outputPath' is required")

        generator = get_generator(family)
        assembly  = generator.generate(params)
        PDFRenderer().render(assembly, output_path)

        return jsonify({'ok': True, 'family': family, 'outputPath': output_path})

    except ValueError as e:
        return _bad_request(str(e))
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/mechanics/families', methods=['GET'])
def mechanicsFamilies():
    """Return the list of available packaging families."""
    from mechanics.families.registry import REGISTRY
    return jsonify({'families': sorted(REGISTRY.keys())})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port,
            debug=app.config['DEBUG'])
