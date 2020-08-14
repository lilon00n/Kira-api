#!/usr/bin/python
#
# PDFlib client: image example in Python
#

from PDFlib.PDFlib import *

imagefile = "nesrin.jpg"

# This is where font/image/PDF input files live. Adjust as necessary.
searchpath = "../data"
p = None

try:
    p = PDFlib()

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return")

    p.set_option("SearchPath={{" + searchpath +"}}")

    if p.begin_document("image.pdf", "") == -1:
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "image")
    p.set_info("Author", "Thomas Merz")
    p.set_info("Title", "image sample")

    image = p.load_image("auto", imagefile, "")
    if image == -1:
        raise Exception("Error: " + p.get_errmsg())

    # dummy page size, will be adjusted by p.fit_image()
    p.begin_page_ext(0, 0, "width=a4.width height=a4.height")
    p.fit_image(image, 0, 0, "adjustpage")
    p.close_image(image)
    p.end_page_ext("")

    p.end_document("")

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname,  ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
