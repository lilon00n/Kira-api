#!/usr/bin/python
#
# PDFlib client: hello example in Python
#

from PDFlib.PDFlib import *

searchpath = "../data"
p = None

try:
    p = PDFlib()

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return")

    # Set the search path for font files
    p.set_option("SearchPath={{" + searchpath +"}}")

    if p.begin_document("hello.pdf", "") == -1:
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Author", "Thomas Merz")
    p.set_info("Creator", "hello.py")
    p.set_info("Title", "Hello world (Python)")

    p.begin_page_ext(0,0, "width=a4.width height=a4.height")
    fontopt = "fontname=NotoSerif-Regular encoding=unicode fontsize=24"
    p.fit_textline("Hello world!", 50, 700, fontopt)
    p.fit_textline("(says Python)",  50, 676, fontopt)

    p.end_page_ext("")

    p.end_document("")     

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
