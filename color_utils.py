# -*- coding: utf-8 -*-
"""
color_utils.py
Replaces make_devicen.py — no PDFlib required.

Converts Lab spot color definitions to ReportLab CMYKColor objects with
a spotName so that ReportLab outputs proper PDF Separation color spaces.
When the PDF is sent to a RIP, each spot color appears on its own plate.
"""

from reportlab.lib.colors import CMYKColor, CMYKColorSep

# Fixed CMYK values for process inks when a file uses DeviceCMYK objects.
# These bypass the Lab→CMYK conversion since the inks are already process colors.
_PROCESS_CMYK = {
    'Cyan':    (1.0, 0.0, 0.0, 0.0),
    'Magenta': (0.0, 1.0, 0.0, 0.0),
    'Yellow':  (0.0, 0.0, 1.0, 0.0),
    'Black':   (0.0, 0.0, 0.0, 1.0),
}


def _lab_to_cmyk(L, a, b):
    """
    Convert CIE L*a*b* (D50) to approximate CMYK for the spot color
    tint-transform fallback rendered in CMYK output devices.

    Returns (c, m, y, k) as floats in [0.0, 1.0].
    """
    # --- Lab → XYZ (D50 reference white: 0.96422, 1.00000, 0.82521) ---
    fy = (L + 16.0) / 116.0
    fx = a / 500.0 + fy
    fz = fy - b / 200.0

    def f_inv(t):
        return t ** 3 if t > 0.2068966 else (t - 16.0 / 116.0) / 7.787

    X = 0.96422 * f_inv(fx)
    Y = 1.00000 * f_inv(fy)
    Z = 0.82521 * f_inv(fz)

    # --- XYZ (D50) → linear sRGB (D65 via Bradford adaptation) ---
    r =  X *  3.1338561 - Y * 1.6168667 - Z * 0.4906146
    g =  X * -0.9787684 + Y * 1.9161415 + Z * 0.0334540
    b_ = X *  0.0719453 - Y * 0.2289914 + Z * 1.4052427

    # Gamma 2.2 compression + clamp
    def _gamma(v):
        v = max(0.0, min(1.0, v))
        return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1.0 / 2.4) - 0.055

    r, g, b_ = _gamma(r), _gamma(g), _gamma(b_)

    # --- sRGB → CMYK (device-independent approximation) ---
    k = 1.0 - max(r, g, b_)
    if k >= 1.0:
        return 0.0, 0.0, 0.0, 1.0
    denom = 1.0 - k
    c = (1.0 - r - k) / denom
    m = (1.0 - g - k) / denom
    y = (1.0 - b_ - k) / denom
    return round(c, 4), round(m, 4), round(y, 4), round(k, 4)


def make_spot_colors(colors):
    """
    Build a dict mapping each ink name to a ReportLab CMYKColor with spotName.

    colors: list of dicts with keys 'name', 'l', 'a', 'ba'

    Returns:
        {color_name: CMYKColor(c, m, y, k, spotName=name)}

    When used with ReportLab, CMYKColor + spotName generates a PDF
    /Separation color space — the correct representation for spot inks.
    """
    result = {}
    for color in colors:
        name = color['name']
        if name in _PROCESS_CMYK:
            c, m, y, k = _PROCESS_CMYK[name]
        else:
            try:
                c, m, y, k = _lab_to_cmyk(
                    float(color.get('l', 0)),
                    float(color.get('a', 0)),
                    float(color.get('ba', 0)),
                )
            except (ValueError, TypeError):
                c, m, y, k = 0.0, 0.0, 0.0, 1.0
        result[name] = CMYKColorSep(c, m, y, k, spotName=name)
    return result


def get_registration_color():
    """
    Returns a registration color that appears on EVERY separation plate.
    Uses PDF /Separation /All — the standard prepress registration ink.
    """
    return CMYKColorSep(1.0, 1.0, 1.0, 1.0, spotName='All')


def get_color_at_tint(spot_color, tint):
    """
    Return a version of the spot color at a different tint level.
    tint: float in [0.0, 1.0]
    """
    return CMYKColorSep(
        spot_color.cyan * tint,
        spot_color.magenta * tint,
        spot_color.yellow * tint,
        spot_color.black * tint,
        spotName=getattr(spot_color, 'spotName', None),
        density=tint,
    )


# Alias used by mark modules that need all-inks / registration colour
def get_all_inks_color(spot_colors):
    """
    Returns the registration color (all inks at 100%).
    For prepress registration marks that must appear on every plate.
    """
    return get_registration_color()


# Legacy alias so existing imports of make_devicen still work during transition
def make_devicen(pdf_unused, colors):
    """
    Drop-in replacement for the old PDFlib make_devicen.
    Returns the spot_colors dict (not a PDFlib device handle).
    """
    return make_spot_colors(colors)
