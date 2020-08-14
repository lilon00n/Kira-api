#!/usr/bin/python
#
# PDFlib client: fill Blocks with PPS to create a business card
# Required software: PPS 9
#

from PDFlib.PDFlib import *

infile = "boilerplate.pdf"

# This is where font/image/PDF input files live. Adjust as necessary.
# Note that this directory must also contain the font files.

searchpath = "../data"

dataset_name = [
 "name",
 "business.title",
 "business.address.line1",
 "business.address.city",
 "business.telephone.voice",
 "business.telephone.fax",
 "business.email",
 "business.homepage" ]

dataset_value = [
 "Victor Kraxi",
 "Chief Paper Officer",
 "17, Aviation Road",
 "Paperfield",
 "phone +1 234 567-89",
 "fax +1 234 567-98",
 "victor@kraxi.com",
 "www.kraxi.com" ]

BLOCKCOUNT = 8

p = None

try:
    p = PDFlib()

    # This means we must check return values of load_font() etc.
    # Set the search path for fonts and PDF files
    p.set_option("errorpolicy=return SearchPath={{" + searchpath +"}}")

    if p.begin_document("businesscard.pdf", "") == -1:
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "businesscard")
    p.set_info("Author", "Thomas Merz")
    p.set_info("Title", "PDFlib Block processing sample")

    blockcontainer = p.open_pdi_document(infile, "")
    if blockcontainer == -1:
        raise Exception("Error: " + p.get_errmsg())

    # Loop over all pages of the input document 
    pagecount = p.pcos_get_number(blockcontainer, "length:pages")

    for pageno in range(1, int(pagecount)+1, 1):

        page = p.open_pdi_page(blockcontainer, pageno, "")
        if page == -1:
            raise Exception("Error: " + p.get_errmsg())

        p.begin_page_ext(20, 20, "")           # dummy page size

        # This will adjust the page size to the size of the input page
        p.fit_pdi_page(page, 0, 0, "adjustpage")

        # Fill all text Blocks with dynamic data
        for i in range(0, BLOCKCOUNT, 1):
            if p.fill_textblock(page, dataset_name[i], dataset_value[i], \
                        "embedding encoding=unicode") == -1:
                print("Warning: " + p.get_errmsg() + "\n")

        p.end_page_ext("")
        p.close_pdi_page(page)

    p.end_document("")
    p.close_pdi_document(blockcontainer)

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
