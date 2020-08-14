#!/usr/bin/python
#
# PDF/X-3 starter:
# Create PDF/X-3 conforming output
#
# Required software: PDFlib/PDFlib+PDI/PPS 9
# Required data: font file, image file, icc profile
#                (see www.pdflib.com for output intent ICC profiles)

from PDFlib.PDFlib import *

def printf(format, *args):
    sys.stdout.write(format % args)

# This is where the data files are. Adjust as necessary.*/
searchpath = "../data"
imagefile = "nesrin.jpg"
outfilename = "starter_pdfx3.pdf"

p = None

try:
    p = PDFlib()

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return")

    p.set_option("SearchPath={{" + searchpath +"}}")

    if (p.begin_document(outfilename, "pdfx=PDF/X-3:2003") == 0):
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_pdfx3")

    # Load output intent ICC profile
    if (p.load_iccprofile("ISOcoated_v2_eci.icc", "usage=outputintent") == -1):
        printf("Error: %s\n", p.get_errmsg())
        printf("See www.pdflib.com for output intent ICC profiles.\n")
        exit(2);


    p.begin_page_ext(0,0, "width=a4.width height=a4.height")

    # font embedding is required for PDF/X
    font = p.load_font("NotoSerif-Regular", "unicode", "embedding")
    if font == -1:
        raise Exception("Error: " + p.get_errmsg())

    p.setfont(font, 24)

    spot = p.makespotcolor("PANTONE 123 C")
    p.setcolor("fill", "spot", spot, 1.0, 0.0, 0.0)
    p.fit_textline("PDF/X-3:2003 starter", 50, 700, "")

    # The RGB image below needs an icc profile; we use sRGB.
    icc = p.load_iccprofile("sRGB", "")

    if (icc == -1):
        raise Exception("Error: " + p.get_errmsg())

    image = p.load_image("auto", imagefile, "iccprofile=" + repr(icc))

    if (image == -1):
        raise Exception("Error: " + p.get_errmsg())

    p.fit_image(image, 0.0, 0.0, "scale=0.5")

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
