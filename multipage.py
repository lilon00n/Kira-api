
import sys
import json
from PDFlib.PDFlib import *
from make_devicen import make_devicen


def make(searchpath, pdffile, outfile, separationsFolder, pathImages):
    paths = outfile.split("\\")
    if len(paths) == 1:
        paths = outfile.split("/")
    p = None

    try:
        p = PDFlib()

        p.set_option("searchpath={" + searchpath + "}")
        # p.set_option("license=w900202-010598-802290-LJJBF2-BEC8G2")

        # This means we must check return values of load_font() etc.
        # This means we must check return values of load_font() etc.
        p.set_option("errorpolicy=return")
        print(pdffile)
        # Open the input PDF */
        indoc = p.open_pdi_document(pdffile, "")
        if indoc == -1:
            print("Error: " + p.get_errmsg())
            next

        pagewidth = p.pcos_get_number(indoc, "pages[0]/width")
        pageheight = p.pcos_get_number(indoc, "pages[0]/height")

        endpage = p.pcos_get_number(indoc, "length:pages")
        pageopen = False
        if p.begin_document(outfile, "") == -1:
            raise "Error: " + p.get_errmsg()

        p.set_info("Creator", "Nala by Verdant Solution")
        page = p.open_pdi_page(indoc, 1, "cloneboxes")
        if page == -1:
            print("Error: " + p.get_errmsg())
            next

        # Start a new page
        if not pageopen:
            p.begin_page_ext(float(pagewidth), float(pageheight), "")
            pageopen = True

        p.fit_pdi_page(page, 0, pageheight, "cloneboxes")

        p.close_pdi_page(page)

        p.end_page_ext("")
        print(separationsFolder)
        # Loop over all pages of the input document
        for image in pathImages:
            tif = p.load_image("tiff", separationsFolder+image, "page=1")
            if tif == -1:
                print("Error: " + p.get_errmsg())
                next

            # Start a new page
            p.begin_page_ext(float(pagewidth), float(pageheight), "")
            p.fit_image(tif, 0.0, 0.0, "adjustpage")
            p.close_image(tif)

            p.end_page_ext("")
            print(image)

        p.close_pdi_document(indoc)

        p.end_document("")

    except PDFlibException as ex:
        print("PDFlib exception occurred:")
        print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

    except Exception as ex:
        print(ex)

    finally:
        if p:
            p.delete()
