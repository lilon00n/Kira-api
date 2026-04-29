# -*- coding: utf-8 -*-
"""
preflight.py
PDF preflight analysis and fix utilities.
"""

import math
import os
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional

import pikepdf
from pikepdf import Array, Name, Pdf, Stream
from pikepdf.models import PdfImage
from PIL import Image as PILImage

ICC_PROFILES = {
    'fogra39':        os.path.join(os.path.dirname(__file__), 'assets', 'icc', 'ISOcoated_v2_eci.icc'),
    'iso_coated_300': os.path.join(os.path.dirname(__file__), 'assets', 'icc', 'ISOcoated_v2_300_eci.icc'),
    'pso_coated_v3':  os.path.join(os.path.dirname(__file__), 'assets', 'icc', 'PSOcoated_v3.icc'),
}
DEFAULT_PROFILE = 'fogra39'


def _resolve_icc(profile_name: str) -> Optional[str]:
    path = ICC_PROFILES.get((profile_name or DEFAULT_PROFILE).lower())
    return path if path and os.path.isfile(path) else None


def _is_white_ish(kind: str, vals: dict) -> bool:
    if kind == 'cmyk':
        return vals['c'] < 0.05 and vals['m'] < 0.05 and vals['y'] < 0.05 and vals['k'] < 0.05
    if kind == 'rgb':
        return vals['r'] > 0.95 and vals['g'] > 0.95 and vals['b'] > 0.95
    if kind == 'gray':
        return vals['g'] > 0.95
    return False


def _detect_white_overprint(pdf: Pdf) -> dict:
    hits = 0
    for page in pdf.pages:
        overprint_fill = False
        fill_kind = None
        fill_vals = {}
        try:
            res = page.get('/Resources')
            ext_gs_dict = (res.get('/ExtGState') if res else None)

            for ins in pikepdf.parse_content_stream(page):
                op = str(ins.operator)
                ops = list(ins.operands)

                if op == 'gs' and ops and ext_gs_dict:
                    try:
                        gs_key = ops[0]
                        if gs_key in ext_gs_dict:
                            gs = ext_gs_dict[gs_key]
                            op_val = gs.get('/op', None)
                            OP_val = gs.get('/OP', None)
                            if op_val is not None:
                                overprint_fill = bool(op_val)
                            elif OP_val is not None:
                                overprint_fill = bool(OP_val)
                            else:
                                overprint_fill = False
                    except Exception:
                        pass

                elif op == 'k' and len(ops) >= 4:
                    fill_kind = 'cmyk'
                    fill_vals = {'c': float(ops[0]), 'm': float(ops[1]), 'y': float(ops[2]), 'k': float(ops[3])}
                elif op == 'rg' and len(ops) >= 3:
                    fill_kind = 'rgb'
                    fill_vals = {'r': float(ops[0]), 'g': float(ops[1]), 'b': float(ops[2])}
                elif op == 'g' and len(ops) >= 1:
                    fill_kind = 'gray'
                    fill_vals = {'g': float(ops[0])}

                if overprint_fill and fill_kind and _is_white_ish(fill_kind, fill_vals):
                    hits += 1
        except Exception:
            pass

    return {'whiteOverprintObjects': hits, 'hasWhiteOverprint': hits > 0}


def _detect_enriched_blacks(pdf: Pdf) -> dict:
    enriched_count = 0
    for page in pdf.pages:
        try:
            for ins in pikepdf.parse_content_stream(page):
                op = str(ins.operator)
                ops = list(ins.operands)
                if op == 'k' and len(ops) >= 4:
                    c, m, y, k = float(ops[0]), float(ops[1]), float(ops[2]), float(ops[3])
                    if k > 0.7:
                        extra = sum(1 for v in [c, m, y] if v > 0.05)
                        if extra >= 2:
                            enriched_count += 1
        except Exception:
            pass
    return {'enrichedBlackObjects': enriched_count, 'hasEnrichedBlack': enriched_count > 0}


def _detect_image_resolutions(pdf: Pdf, max_dpi: float = 300.0) -> dict:
    high_res_images = 0
    image_count = 0
    visited: set = set()

    for page in pdf.pages:
        try:
            mediabox = page.get('/MediaBox')
            if mediabox is None:
                continue
            page_w_in = (float(mediabox[2]) - float(mediabox[0])) / 72.0
            page_h_in = (float(mediabox[3]) - float(mediabox[1])) / 72.0
            if page_w_in <= 0 or page_h_in <= 0:
                continue

            res = page.get('/Resources')
            xobjects = res.get('/XObject') if res else None
            if not xobjects:
                continue

            for k in xobjects:
                xobj = xobjects[k]
                if not isinstance(xobj, Stream) or xobj.get('/Subtype') != Name.Image:
                    continue
                try:
                    og = xobj.objgen
                    key = (int(og[0]), int(og[1]))
                except Exception:
                    key = id(xobj)
                if key in visited:
                    continue
                visited.add(key)

                w_obj = xobj.get('/Width')
                h_obj = xobj.get('/Height')
                if w_obj is None or h_obj is None:
                    continue
                iw, ih = int(w_obj), int(h_obj)
                image_count += 1

                eff_dpi = min(iw / page_w_in, ih / page_h_in)
                if eff_dpi > max_dpi * 1.25:
                    high_res_images += 1
        except Exception:
            pass

    return {
        'imageCount': image_count,
        'highResImages': high_res_images,
        'hasHighResImages': high_res_images > 0,
    }


def _detect_non_embedded_fonts(pdf: Pdf) -> dict:
    non_embedded = []
    seen: set = set()

    for objid in range(1, len(pdf.objects) + 1):
        try:
            obj = pdf.get_object((objid, 0))
            if not isinstance(obj, dict) or obj.get('/Type') != Name.Font:
                continue
            name_obj = obj.get('/BaseFont')
            if name_obj is None:
                continue
            font_name = str(name_obj).lstrip('/')
            if font_name in seen:
                continue
            seen.add(font_name)

            descriptor = obj.get('/FontDescriptor')
            if descriptor is None:
                non_embedded.append(font_name)
                continue
            has_file = (
                descriptor.get('/FontFile') is not None
                or descriptor.get('/FontFile2') is not None
                or descriptor.get('/FontFile3') is not None
            )
            if not has_file:
                non_embedded.append(font_name)
        except Exception:
            pass

    return {
        'nonEmbeddedFonts': non_embedded,
        'hasNonEmbeddedFonts': len(non_embedded) > 0,
    }


def analyze_pdf(pdf_path: str, max_dpi: float = 300.0) -> dict:
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f'File not found: {pdf_path}')

    from services.pdf_inks.extract_inks import (
        _detect_rgb_content,
        _detect_pure_black_text,
        _detect_transparency,
        _find_separations,
        _key_for_process,
        _is_reserved_spot,
    )

    with Pdf.open(pdf_path) as pdf:
        rgb_content    = _detect_rgb_content(pdf)
        pure_black     = _detect_pure_black_text(pdf)
        transparency   = _detect_transparency(pdf)
        white_op       = _detect_white_overprint(pdf)
        enriched_black = _detect_enriched_blacks(pdf)
        image_res      = _detect_image_resolutions(pdf, max_dpi)
        fonts          = _detect_non_embedded_fonts(pdf)

        spots = []
        spots_set: set = set()
        for sep_name, _ in _find_separations(pdf):
            if _key_for_process(sep_name) or _is_reserved_spot(sep_name):
                continue
            if sep_name not in spots_set:
                spots.append(sep_name)
                spots_set.add(sep_name)

    has_rgb = (
        rgb_content['rgbImages'] + rgb_content['iccBasedRgb'] + rgb_content['rgbVectors']
    ) > 0

    issues = []
    if has_rgb:
        issues.append({
            'code': 'RGB_CONTENT', 'severity': 'error',
            'message': (
                f"Contenido RGB encontrado: {rgb_content['rgbImages']} imagen(es), "
                f"{rgb_content['rgbVectors']} objeto(s) vectoriales"
            ),
        })
    if white_op['hasWhiteOverprint']:
        issues.append({
            'code': 'WHITE_OVERPRINT', 'severity': 'warning',
            'message': f"{white_op['whiteOverprintObjects']} objeto(s) blanco(s) con sobreimpresión activada",
        })
    if enriched_black['hasEnrichedBlack']:
        issues.append({
            'code': 'ENRICHED_BLACK', 'severity': 'warning',
            'message': f"{enriched_black['enrichedBlackObjects']} negro(s) enriquecido(s) detectado(s)",
        })
    if fonts['hasNonEmbeddedFonts']:
        names_preview = ', '.join(fonts['nonEmbeddedFonts'][:5])
        issues.append({
            'code': 'NON_EMBEDDED_FONTS', 'severity': 'error',
            'message': f"Fuentes no embebidas: {names_preview}",
        })
    if image_res['hasHighResImages']:
        issues.append({
            'code': 'HIGH_RES_IMAGES', 'severity': 'info',
            'message': f"{image_res['highResImages']} imagen(es) pueden superar {int(max_dpi)} DPI",
        })

    return {
        'ok': True,
        'issues': issues,
        'hasIssues': len(issues) > 0,
        'rgbContent': rgb_content,
        'pureBlackText': pure_black,
        'transparency': transparency,
        'whiteOverprint': white_op,
        'enrichedBlack': enriched_black,
        'imageResolution': image_res,
        'fonts': fonts,
        'spots': spots,
    }


def fix_pdf(pdf_path: str, out_path: str, options: dict, icc_profile: str = DEFAULT_PROFILE) -> dict:
    """
    Apply preflight fixes and save to out_path.
    options keys: convertRgb, outlineFonts, downsampleImages, maxDpi
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f'File not found: {pdf_path}')

    icc_path = _resolve_icc(icc_profile)
    applied = []
    tmp_files = []
    working = pdf_path

    try:
        if options.get('convertRgb', True):
            from services.pdf_inks.extract_inks import convert_rgb_to_cmyk_selective
            fd, tmp = tempfile.mkstemp(suffix='_rgb2cmyk.pdf')
            os.close(fd)
            tmp_files.append(tmp)
            result = convert_rgb_to_cmyk_selective(working, tmp, icc_path)
            conv = result.get('converted', {})
            total = conv.get('rgbVectorsConverted', 0) + conv.get('rgbImagesConverted', 0)
            applied.append({'fix': 'convertRgb', 'converted': total, 'iccProfile': icc_profile})
            working = tmp

        if options.get('downsampleImages', False):
            max_dpi = float(options.get('maxDpi', 300))
            fd, tmp2 = tempfile.mkstemp(suffix='_downsample.pdf')
            os.close(fd)
            tmp_files.append(tmp2)
            count = _downsample_images(working, tmp2, max_dpi)
            applied.append({'fix': 'downsampleImages', 'count': count, 'maxDpi': max_dpi})
            working = tmp2

        if options.get('outlineFonts', False):
            fd, tmp3 = tempfile.mkstemp(suffix='_outline.pdf')
            os.close(fd)
            tmp_files.append(tmp3)
            _outline_fonts_gs(working, tmp3)
            applied.append({'fix': 'outlineFonts'})
            working = tmp3

        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        shutil.copy2(working, out_path)

    finally:
        for f in tmp_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except Exception:
                pass

    return {
        'ok': True,
        'outPath': out_path,
        'appliedFixes': applied,
        'fixCount': len(applied),
    }


def _render_sizes_from_page(page) -> dict:
    """
    Parse page content stream and return {xobj_name: (rendered_w_pts, rendered_h_pts)}.
    Uses the largest rendered size when an image appears multiple times (conservative:
    avoids over-downsampling shared images placed at different scales).
    """
    sizes = {}
    try:
        instructions = list(pikepdf.parse_content_stream(page))
    except Exception:
        return sizes

    ctm_stack = []
    ctm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]  # identity

    def concat(cur, m):
        # CTM_new = m × CTM_old  (PDF spec: cm premultiplies the CTM)
        a1, b1, c1, d1, e1, f1 = cur
        a2, b2, c2, d2, e2, f2 = m
        return [
            a2 * a1 + b2 * c1,
            a2 * b1 + b2 * d1,
            c2 * a1 + d2 * c1,
            c2 * b1 + d2 * d1,
            e2 * a1 + f2 * c1 + e1,
            e2 * b1 + f2 * d1 + f1,
        ]

    for ins in instructions:
        op = str(ins.operator)
        operands = list(ins.operands)
        if op == 'q':
            ctm_stack.append(ctm[:])
        elif op == 'Q':
            if ctm_stack:
                ctm = ctm_stack.pop()
        elif op == 'cm' and len(operands) == 6:
            try:
                ctm = concat(ctm, [float(v) for v in operands])
            except Exception:
                pass
        elif op == 'Do' and operands:
            name = str(operands[0])
            a, b, c, d = ctm[0], ctm[1], ctm[2], ctm[3]
            rw = math.sqrt(a * a + b * b)
            rh = math.sqrt(c * c + d * d)
            if rw > 0 and rh > 0:
                if name not in sizes:
                    sizes[name] = (rw, rh)
                else:
                    pw, ph = sizes[name]
                    sizes[name] = (max(pw, rw), max(ph, rh))
    return sizes


def _downsample_images(pdf_path: str, out_path: str, max_dpi: float) -> int:
    downsampled = 0
    visited: set = set()

    with Pdf.open(pdf_path) as pdf:
        for page in pdf.pages:
            try:
                mediabox = page.get('/MediaBox')
                if mediabox is None:
                    continue
                page_w_in = (float(mediabox[2]) - float(mediabox[0])) / 72.0
                page_h_in = (float(mediabox[3]) - float(mediabox[1])) / 72.0
                if page_w_in <= 0 or page_h_in <= 0:
                    continue

                render_sizes = _render_sizes_from_page(page)

                res = page.get('/Resources')
                xobjects = res.get('/XObject') if res else None
                if not xobjects:
                    continue

                for k in xobjects:
                    xobj = xobjects[k]
                    if not isinstance(xobj, Stream) or xobj.get('/Subtype') != Name.Image:
                        continue
                    try:
                        og = xobj.objgen
                        key = (int(og[0]), int(og[1]))
                    except Exception:
                        key = id(xobj)
                    if key in visited:
                        continue
                    visited.add(key)

                    try:
                        w = int(xobj.get('/Width', 0))
                        h = int(xobj.get('/Height', 0))
                        bpc = int(xobj.get('/BitsPerComponent', 8))
                        if bpc != 8 or w <= 0 or h <= 0:
                            continue
                        if (xobj.get('/SMask') is not None
                                or xobj.get('/Mask') is not None
                                or bool(xobj.get('/ImageMask', False))):
                            continue

                        xname = str(k)
                        if xname in render_sizes:
                            rw_pts, rh_pts = render_sizes[xname]
                            eff_dpi = min(w / (rw_pts / 72.0), h / (rh_pts / 72.0))
                        else:
                            eff_dpi = min(w / page_w_in, h / page_h_in)

                        if eff_dpi <= max_dpi * 1.25:
                            continue

                        try:
                            img = PdfImage(xobj).as_pil_image()
                        except Exception:
                            continue

                        cs = xobj.get('/ColorSpace')
                        if cs == Name.DeviceCMYK or img.mode == 'CMYK':
                            img = img.convert('CMYK') if img.mode != 'CMYK' else img
                            out_cs = Name.DeviceCMYK
                        elif cs == Name.DeviceGray or img.mode == 'L':
                            img = img.convert('L') if img.mode != 'L' else img
                            out_cs = Name.DeviceGray
                        else:
                            img = img.convert('RGB')
                            out_cs = Name.DeviceRGB

                        scale = max_dpi / eff_dpi
                        new_w = max(1, int(w * scale))
                        new_h = max(1, int(h * scale))
                        img_r = img.resize((new_w, new_h), PILImage.LANCZOS)

                        xobj.write(img_r.tobytes(), filter=Name.FlateDecode)
                        xobj['/Width'] = new_w
                        xobj['/Height'] = new_h
                        xobj['/ColorSpace'] = out_cs
                        if '/DecodeParms' in xobj:
                            del xobj['/DecodeParms']
                        downsampled += 1
                    except Exception:
                        pass
            except Exception:
                pass

        pdf.save(out_path, object_stream_mode=pikepdf.ObjectStreamMode.disable)

    return downsampled


def _restore_pdf_boxes(original_path: str, target_path: str):
    """Copy TrimBox/BleedBox/CropBox/ArtBox from original into target PDF (in-place)."""
    fd, tmp = tempfile.mkstemp(suffix='_restored.pdf')
    os.close(fd)
    try:
        with Pdf.open(original_path) as orig:
            with Pdf.open(target_path) as target:
                for orig_page, tgt_page in zip(orig.pages, target.pages):
                    for box in ('/TrimBox', '/BleedBox', '/CropBox', '/ArtBox'):
                        val = orig_page.get(box)
                        if val is not None:
                            tgt_page[box] = val
                target.save(tmp, object_stream_mode=pikepdf.ObjectStreamMode.disable)
        shutil.move(tmp, target_path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def _outline_fonts_gs(pdf_path: str, out_path: str):
    from set_trimbox import _find_gs
    gs = _find_gs()
    fd, tmp = tempfile.mkstemp(suffix='_gs_outline.pdf')
    os.close(fd)
    try:
        cmd = [
            gs, '-dBATCH', '-dNOPAUSE', '-dQUIET',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.3',
            '-dNoOutputFonts',
            f'-sOutputFile={tmp}',
            pdf_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            raise RuntimeError(f'GS font outlining failed: {result.stderr[:300]}')
        # GhostScript strips TrimBox/BleedBox — restore from original
        _restore_pdf_boxes(pdf_path, tmp)
        shutil.move(tmp, out_path)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
