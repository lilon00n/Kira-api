# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec para kira-api — Python 3.13, PyInstaller >= 6.0
# Modo onedir: genera dist/apipy/apipy.exe + _internal/ con todas las DLLs.
# Más rápido de arrancar que onefile y mejor para un servidor Flask en producción.
#
# Uso:
#   venv-new\Scripts\pip install pyinstaller
#   venv-new\Scripts\pyinstaller apipy.spec

import os
import sys

basedir = os.path.dirname(os.path.abspath(SPEC))

# OpenCV, reportlab y numpy tienen módulos internos que PyInstaller no detecta
# automáticamente. Los listamos explícitamente.
hidden = [
    # Flask + Werkzeug
    'flask', 'werkzeug', 'werkzeug.routing', 'werkzeug.serving',
    'werkzeug.exceptions', 'werkzeug.middleware',
    'jinja2', 'markupsafe',
    'click',
    # Pillow (PIL)
    'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
    'PIL.TiffImagePlugin', 'PIL.JpegImagePlugin', 'PIL.PngImagePlugin',
    # reportlab
    'reportlab', 'reportlab.pdfgen', 'reportlab.pdfgen.canvas',
    'reportlab.lib', 'reportlab.lib.colors', 'reportlab.lib.units',
    'reportlab.graphics', 'reportlab.platypus',
    'reportlab.rl_config', 'reportlab.pdfbase',
    'reportlab.pdfbase.ttfonts', 'reportlab.pdfbase.pdfmetrics',
    # pypdf
    'pypdf', 'pypdf.generic', 'pypdf.filters',
    # numpy
    'numpy', 'numpy.core', 'numpy.core._multiarray_umath',
    'numpy.lib', 'numpy.linalg', 'numpy.fft',
    # OpenCV — la mayoría de imports internos son C-extensions; solo necesitamos el top-level
    'cv2',
    # python-dotenv
    'dotenv',
]

a = Analysis(
    ['api.py'],
    pathex=[basedir],
    binaries=[],
    datas=[
        # Incluir carpetas de datos que Kira pueda necesitar en runtime
        (os.path.join(basedir, 'data'), 'data'),
    ] if os.path.isdir(os.path.join(basedir, 'data')) else [],
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos de test y dev que no se necesitan en producción
        'pytest', 'unittest', 'distutils', 'pip', 'setuptools',
        'tkinter', 'matplotlib',
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='apipy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['vcruntime*.dll', 'msvcp*.dll', 'api-ms-win*.dll'],
    console=True,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=['vcruntime*.dll', 'msvcp*.dll', 'api-ms-win*.dll'],
    name='apipy',
)
