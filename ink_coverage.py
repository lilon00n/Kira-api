# -*- coding: utf-8 -*-
"""
ink_coverage.py
Calcula el porcentaje de cobertura de tinta por canal spot en un PDF/AI.

Usa Ghostscript (tiffsep) para generar separaciones por canal,
luego numpy para medir qué fracción de pixels tiene tinta.

Requiere:
  - Ghostscript 10+ instalado en C:\\Program Files\\gs
  - numpy (venv-new lo tiene)

Uso directo:
  python ink_coverage.py input/1circular_etiq.ai
"""

import os
import sys
import glob
import shutil
import tempfile
import subprocess
import numpy as np

GS_EXE = r"C:\Program Files\gs\gs10.07.0\bin\gswin64c.exe"


def _find_gs():
    """Locate gswin64c.exe — searches common install paths."""
    candidates = [
        GS_EXE,
        r"C:\Program Files (x86)\gs\gs10.07.0\bin\gswin64c.exe",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    # Walk C:\Program Files\gs\ looking for any version
    gs_root = r"C:\Program Files\gs"
    if os.path.isdir(gs_root):
        for entry in sorted(os.listdir(gs_root), reverse=True):
            exe = os.path.join(gs_root, entry, "bin", "gswin64c.exe")
            if os.path.exists(exe):
                return exe
    return None


def _normalize_name(raw: str) -> str:
    """Ghostscript encodes the separation TIFF filename as the ink name
    with spaces replaced by underscores and surrounded by parens stripped."""
    # GS names the file: <PageN>.<inkname>.tif
    # e.g. "PANTONE 261 C" → file contains "PANTONE_261_C" in the name
    pass


def calculate_coverage(pdf_path: str, color_names: list, resolution: int = 72) -> dict:
    """
    Rasterize each Separation channel and measure ink coverage (0–100 %).

    Parameters
    ----------
    pdf_path    : path to PDF or AI file (page 1 only)
    color_names : list of spot color names expected (e.g. ['PANTONE 261 C'])
    resolution  : rasterization DPI (72 is fine for coverage calculation)

    Returns
    -------
    dict  {color_name: coverage_percent_string}
    e.g.  {'PANTONE 261 C': '34.52', 'PANTONE 192 C': '12.08'}
    """
    gs = _find_gs()
    if gs is None:
        print("  [ink_coverage] Ghostscript no encontrado — cobertura = 0%")
        return {n: "0" for n in color_names}

    tmpdir = tempfile.mkdtemp(prefix="sep_")
    try:
        out_pattern = os.path.join(tmpdir, "page%d.tif")
        cmd = [
            gs,
            "-dBATCH",
            "-dNOPAUSE",
            "-dQUIET",
            "-sDEVICE=tiffsep",
            f"-r{resolution}",
            "-dFirstPage=1",
            "-dLastPage=1",
            "-dUseTrimBox",   # measure only within the TrimBox, not bleed
            f"-sOutputFile={out_pattern}",
            os.path.abspath(pdf_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"  [ink_coverage] GS error: {result.stderr[:300]}")
            return {n: "0" for n in color_names}

        # Discover generated TIFFs — GS creates one per channel
        tif_files = glob.glob(os.path.join(tmpdir, "*.tif"))

        # Build a map: normalized-lower-name → filepath
        tif_map = {}
        for tf in tif_files:
            base = os.path.splitext(os.path.basename(tf))[0]
            # GS filename pattern: "page1(PANTONE 261 C)" or "page1.PANTONE.261.C"
            # The ink name portion is after the first dot or inside parens
            name_part = base
            if "(" in name_part and ")" in name_part:
                name_part = name_part[name_part.index("(") + 1 : name_part.rindex(")")]
            elif "." in name_part:
                # Remove page prefix: "page1.PANTONE 261 C" → "PANTONE 261 C"
                name_part = name_part.split(".", 1)[-1] if "." in name_part else name_part
            tif_map[name_part.lower().strip()] = tf

        coverage = {}
        for name in color_names:
            key = name.lower().strip()
            tif_path = tif_map.get(key)
            if tif_path is None:
                # Try partial match (GS sometimes truncates)
                for k, v in tif_map.items():
                    if key in k or k in key:
                        tif_path = v
                        break

            if tif_path and os.path.exists(tif_path):
                img = np.frombuffer(
                    open(tif_path, "rb").read(), dtype=np.uint8
                )
                # Read as grayscale via basic TIFF strip (numpy approach)
                try:
                    from PIL import Image
                    im = Image.open(tif_path).convert("L")
                    arr = np.array(im, dtype=np.float32)
                    # In tiffsep: 0 = full ink, 255 = no ink
                    ink_frac = 1.0 - float(np.mean(arr / 255.0))
                    coverage[name] = f"{ink_frac * 100:.2f}"
                except ImportError:
                    # PIL not available — use cv2
                    import cv2
                    im = cv2.imread(tif_path, cv2.IMREAD_GRAYSCALE)
                    if im is not None:
                        ink_frac = 1.0 - float(np.mean(im.astype(np.float32) / 255.0))
                        coverage[name] = f"{ink_frac * 100:.2f}"
                    else:
                        coverage[name] = "0"
            else:
                print(f"  [ink_coverage] Canal '{name}' no encontrado en separaciones")
                print(f"  Archivos generados: {[os.path.basename(t) for t in tif_files]}")
                coverage[name] = "0"

        # ---- Detect process CMYK channels (GS always generates them) ----
        # GS names them: Cyan, Magenta, Yellow, Black (or Black(K))
        _PROCESS_ALIASES = {
            'Cyan':    ['cyan'],
            'Magenta': ['magenta'],
            'Yellow':  ['yellow'],
            'Black':   ['black', 'black(k)'],
        }
        for ink_name, aliases in _PROCESS_ALIASES.items():
            if ink_name in coverage:
                continue   # already measured (e.g., file has a /Separation called 'Cyan')
            for alias in aliases:
                tif_path = tif_map.get(alias)
                if tif_path and os.path.exists(tif_path):
                    try:
                        from PIL import Image
                        im = Image.open(tif_path).convert("L")
                        arr = np.array(im, dtype=np.float32)
                        ink_frac = 1.0 - float(np.mean(arr / 255.0))
                        coverage[ink_name] = f"{ink_frac * 100:.2f}"
                    except Exception:
                        coverage[ink_name] = "0"
                    break

        return coverage

    except subprocess.TimeoutExpired:
        print("  [ink_coverage] Timeout al ejecutar Ghostscript")
        return {n: "0" for n in color_names}
    except Exception as e:
        print(f"  [ink_coverage] Error: {e}")
        return {n: "0" for n in color_names}
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "input/1circular_etiq.ai"
    # Auto-read spot names
    from read_spots import extract_spots_from_pdf
    spots = extract_spots_from_pdf(path)
    names = [s["name"] for s in spots]
    print(f"Calculando cobertura para: {names}")
    cov = calculate_coverage(path, names)
    for name, pct in cov.items():
        print(f"  {name:30s}  {pct}%")
