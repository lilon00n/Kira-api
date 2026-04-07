# -*- coding: utf-8 -*-
"""
read_spots.py
Reads spot color names AND their Lab values directly from a PDF/AI file.
The /Separation colorspace tint function stores the Lab coordinates of each ink.

C1 in the FunctionType 2 = [L, a, b] of the ink at 100% (full tint).
C0 = [100, 0, 0] = paper (Lab white).
"""

import sys
import math
from pypdf import PdfReader


def _cmyk_to_lab(c, m, y, k):
    """Convert CMYK [0-1] → approximate CIE L*a*b* (D50).
    Used when Illustrator stores /Separation with /DeviceCMYK alternate space."""
    r = (1.0 - c) * (1.0 - k)
    g = (1.0 - m) * (1.0 - k)
    b = (1.0 - y) * (1.0 - k)
    # sRGB gamma expand
    def lin(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = lin(r), lin(g), lin(b)
    # sRGB D65 -> XYZ D65
    X = r * 0.4124 + g * 0.3576 + b * 0.1805
    Y = r * 0.2126 + g * 0.7152 + b * 0.0722
    Z = r * 0.0193 + g * 0.1192 + b * 0.9505
    # D65 -> D50 Bradford
    Xn, Yn, Zn = 0.96422, 1.00000, 0.82521
    X /= Xn; Y /= Yn; Z /= Zn
    def f(t):
        return t ** (1/3) if t > 0.008856 else 7.787 * t + 16/116
    L = 116 * f(Y) - 16
    a = 500 * (f(X) - f(Y))
    bv = 200 * (f(Y) - f(Z))
    return round(L, 2), round(a, 2), round(bv, 2)


def extract_spots_from_pdf(filepath):
    """
    Returns list of dicts: [{name, l, a, ba}, ...] extracted from
    /Separation colorspace Lab tint functions embedded in the PDF.
    """
    reader = PdfReader(filepath)
    page = reader.pages[0]
    res = page.get("/Resources", {})

    spots = {}

    def _try_extract_cs(cs_dict):
        if not cs_dict:
            return
        for key in cs_dict.keys():
            try:
                arr = list(cs_dict[key])
                if len(arr) < 4 or str(arr[0]) != "/Separation":
                    continue
                name = str(arr[1]).lstrip("/")
                if name in spots or name.lower() in ("all", "none"):
                    continue
                # arr[3] is the tint transform function
                fn = arr[3] if len(arr) > 3 else None
                if fn is None:
                    continue
                fn_obj = dict(fn)
                if "/C1" in fn_obj:
                    c1 = [float(v) for v in fn_obj["/C1"]]
                    # Detect alternate colorspace: arr[2] is /DeviceCMYK or [/Lab, ...]
                    alt = arr[2] if len(arr) > 2 else None
                    alt_str = str(alt) if alt is not None else ""
                    is_cmyk = "DeviceCMYK" in alt_str or (
                        "CMYK" in alt_str and "Lab" not in alt_str
                    )
                    if is_cmyk and len(c1) >= 4:
                        # c1 is [C, M, Y, K] — convert to Lab for display
                        lv, av, bv = _cmyk_to_lab(c1[0], c1[1], c1[2], c1[3])
                        spots[name] = {
                            "name": name,
                            "l": lv, "a": av, "ba": bv,
                        }
                        continue
                    elif len(c1) >= 3:
                        # c1 is [L, a, b]
                        spots[name] = {
                            "name": name,
                            "l":  round(c1[0], 2),
                            "a":  round(c1[1], 2),
                            "ba": round(c1[2], 2),
                        }
                        continue
                # If no C1, add without Lab (will fall back to black)
                if name not in spots:
                    spots[name] = {"name": name, "l": "0", "a": "0", "ba": "0"}
            except Exception:
                pass

    # Check page-level ColorSpace resources
    if "/ColorSpace" in res:
        _try_extract_cs(res["/ColorSpace"])

    # Check XObject-level resources (embedded Form XObjects)
    if "/XObject" in res:
        xo = res["/XObject"]
        for xk in xo.keys():
            try:
                xobj = xo[xk]
                xr = xobj.get("/Resources", {})
                if "/ColorSpace" in xr:
                    _try_extract_cs(xr["/ColorSpace"])
            except Exception:
                pass

    # Exclude die-cut technical colors (not printed inks)
    skip_names = {"die", "Die", "DIE", "die cut", "Die Cut", "Dieline", "dieline"}
    return [v for k, v in spots.items() if k not in skip_names]


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "input/1circular_etiq.ai"
    results = extract_spots_from_pdf(path)
    print(f"\nSpot colors found in: {path}")
    for s in results:
        print(f"  {s['name']:30s}  L={s['l']:6}  a={s['a']:7}  b={s['ba']:7}")
    print()
