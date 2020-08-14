#!/usr/bin/python
# PDFlib Virtual File system (PVF):
# Create a PVF file which holds an image or PDF, and import the data from the
# PVF file
#
# This avoids disk access and is especially useful when the same image or PDF
# is imported multiply. For examples, images which sit in a database don't
# have to be written and re-read from disk, but can be passed to PDFlib
# directly in memory. A similar technique can be used for loading other data
# such as fonts, ICC profiles, etc.
#
# Required software: PDFlib/PDFlib+PDI/PPS 9
# Required data: image file

# This is where the data files are. Adjust as necessary.
searchpath = "../data"
outfile = "starter_pvf.pdf"

from PDFlib.PDFlib import *

p = None

try:
    p = PDFlib()

    p.set_option("SearchPath={{" + searchpath +"}}")

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return")

    # Set an output path according to the name of the topic
    if p.begin_document(outfile, "") == -1:
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_pvf")

    # We just read some image data from a file; to really benefit
    # from using PVF read the data from a Web site or a database instead
    f = open("../data/PDFlib-logo.tif", "rb")
    f.seek(0, 2)
    filelen = f.tell()
    f.seek(0, 0)
    imagedata = f.read(filelen)


    p.create_pvf("/pvf/image", imagedata, "")

    # Load the image from the PVF
    image = p.load_image("auto", "/pvf/image", "")
    if image == -1:
        raise Exception("Error: " + p.get_errmsg())

    # Fit the image on page 1
    p.begin_page_ext(0,0, "width=a4.width height=a4.height")

    p.fit_image(image, 350, 750, "")

    p.end_page_ext("")

    # Fit the image on page 2
    p.begin_page_ext(0,0, "width=a4.width height=a4.height")

    p.fit_image(image, 350, 50, "")

    p.end_page_ext("")

    # Delete the virtual file to free the allocated memory
    p.delete_pvf("/pvf/image")

    p.end_document("")

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
