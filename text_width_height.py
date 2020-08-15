#!/usr/bin/python
#
# PDF impose:
# Import all pages from one more existing PDFs, and place col x row pages 
# on each sheet of the output PDF (imposition).
# 
# Required software: PDFlib+PDI/PPS 9
# Required data: PDF documents
#


# This is where the data files are. Adjust as necessary. 
searchpath = '../../../worksDir'
title = "Nombre de colores"
import sys

text = sys.argv[1]
fsize = sys.argv[2]
angle = sys.argv[3]

from PDFlib.PDFlib import *

p = None

try:
    p = PDFlib()

    p.set_option("searchpath={" + searchpath + "}")

    # This means we must check return values of load_font() etc. 
    p.set_option("errorpolicy=return")
    # Open the input document
    if p.begin_document("test.pdf", "") == -1:
        raise "Error: " + p.get_errmsg()

    optlist = "fontname=Helvetica fontsize=" + fsize+ " encoding=unicode rotate="+ angle

    textwidth = p.info_textline(text, "width", optlist)
    textheight = p.info_textline(text, "height", optlist)
    print(textwidth)
    print(textheight)
    p.end_document("")
    

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
