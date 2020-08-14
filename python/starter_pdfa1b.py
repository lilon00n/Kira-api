#!/usr/bin/python
#
# PDF/A-1b starter:
# Create PDF/A-1b conforming output
#
# required software: PDFlib/PDFlib+PDI/PPS 9
# required data: font file, image file

from PDFlib.PDFlib import *

# This is where the data files are. Adjust as necessary.
searchpath = "../data"
imagefile = "nesrin.jpg"
outfilename = "starter_pdfa1b.pdf"

p = None

try:
    p = PDFlib()

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return")

    p.set_option("SearchPath={{" + searchpath +"}}")

    # PDF/A-1a requires Tagged PDF
    if (p.begin_document(outfilename, "pdfa=PDF/A-1b:2005") == -1):
        raise Exception("Error: " + p.get_errmsg())

    #
    # We use sRGB as output intent since it allows the color
    # spaces CIELab, ICC-based, grayscale, and RGB.
    #
    # If you need CMYK color you must use a CMYK output profile.


    if (p.load_iccprofile("sRGB", "usage=outputintent") == -1):
        raise Exception("Error: " + p.get_errmsg() + "\n" +
            "See www.pdflib.com for output intent ICC profiles.") 

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_pdfa1b")

    p.begin_page_ext(0,0, "width=a4.width height=a4.height")

    # font embedding is required for PDF/A
    font = p.load_font("NotoSerif-Regular", "unicode", "embedding")
    if font == -1:
        raise Exception("Error: " + p.get_errmsg())

    p.setfont(font, 24)

    p.fit_textline("PDF/A-1b:2005 starter", 50, 700, "")

    # We can use an RGB image since we already supplied an
    # output intent profile.

    image = p.load_image("auto", imagefile, "")
    if (image == -1):
        raise Exception("Error: " + p.get_errmsg())

    # Place the image at the bottom of the page
    p.fit_image(image, 0.0, 0.0, "scale=0.5")

    p.end_page_ext("")
    p.close_image(image)

    p.end_document("")

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
