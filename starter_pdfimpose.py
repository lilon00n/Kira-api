#!/usr/bin/python
#
# PDF impose:
# Import all pages from one more existing PDFs, and place col x row pages
# on each sheet of the output PDF (imposition).
#
# Required software: PDFlib+PDI/PPS 9
# Required data: PDF documents
#

from PDFlib.PDFlib import *


def impose(outfile):
    # This is where the data files are. Adjust as necessary.
    searchpath = './data'
    #outfile = "starter_pdfimpose.pdf"
    title = "PDF Impose"

    pdffiles = [
        "PDFlib-datasheet.pdf",
        "PLOP-datasheet.pdf",
        "pCOS-datasheet.pdf"
    ]
    col = 0
    row = 0
    scale = 1          # scaling factor of a page
    rowheight = 0      # row height for the page to be placed
    olwidth = 0        # column width for the page to be placed
    sheetwidth = 595   # width of the sheet
    sheetheight = 842  # height of the sheet
    maxcols = 3        # maxcols x maxrows pages will be placed on one sheet
    maxrows = 4

    p = None

    try:
        p = PDFlib()

        p.set_option("searchpath={" + searchpath + "}")

        # This means we must check return values of load_font() etc.
        p.set_option("errorpolicy=return")

        if p.begin_document(outfile, "") == -1:
            raise "Error: " + p.get_errmsg()

        p.set_info("Creator", "Nala by Verdant Solution")
        p.set_info("Title", title)

        # ---------------------------------------------------------------------
        # Define the sheet width and height, the number of maxrows and columns
        # and calculate the scaling factor and cell dimensions for the
        # multi-page imposition.
        # ---------------------------------------------------------------------

        if maxrows > maxcols:
            scale = 1.0 / maxrows
        else:
            scale = 1.0 / maxcols

        rowheight = sheetheight * scale
        colwidth = sheetwidth * scale

        # is a page open that must be closed?
        pageopen = False

        # Loop over all input documents
        for pdffile in (pdffiles):

            # Open the input PDF */
            indoc = p.open_pdi_document(pdffile, "")
            if indoc == -1:
                print("Error: " + p.get_errmsg())
                next

            endpage = p.pcos_get_number(indoc, "length:pages")

            # Loop over all pages of the input document
            for pageno in range(1, int(endpage)+1, 1):
                page = p.open_pdi_page(indoc, pageno, "")

                if page == -1:
                    print("Error: " + p.get_errmsg())
                    next

                # Start a new page
                if not pageopen:
                    p.begin_page_ext(sheetwidth, sheetheight, "")
                    pageopen = True

                # The save/restore pair is required to get an independent
                # clipping area for each mini page. Note that clipping
                # is not required for the imported pages, but affects
                # the rectangle around each page. Without clipping we
                # would have to move the rectangle a bit inside the
                # imported page to avoid drawing outside its area.

                p.save()

                # Clipping path for the rectangle
                p.rect(col * colwidth, sheetheight - (row + 1) * rowheight,
                       colwidth, rowheight)
                p.clip()

                optlist = "boxsize {" + str(colwidth) + \
                    " " + str(rowheight) + "} fitmethod meet"

                p.fit_pdi_page(page, col * colwidth, sheetheight -
                               (row + 1) * rowheight, optlist)

                p.close_pdi_page(page)

                # Draw a frame around the mini page */
                p.set_graphics_option("linewidth=" + str(scale))
                p.rect(col * colwidth, sheetheight - (row + 1)
                       * rowheight, colwidth, rowheight)
                p.stroke()

                p.restore()
                # Start a new row if the current row is full

                col += 1
                if col == maxcols:
                    col = 0
                    row += 1

                # Close the page if it is full
                if row == maxrows:
                    row = 0
                    p.end_page_ext("")
                    pageopen = false
            p.close_pdi_document(indoc)

        if pageopen:
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
