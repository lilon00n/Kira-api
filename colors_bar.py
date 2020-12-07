import sys
from PDFlib.PDFlib import *
import json
from make_devicen import make_devicen


def make(searchpath, pdffile, outfile, colors, intensities, size, x, y, place, sideX, sideY):
    paths = outfile.split("\\")
    if len(paths) == 1:
        paths = outfile.split("/")
    title = paths[len(paths)-1]
    intensities = intensities.split(',')
    x = float(x)
    y = float(y)
    size = float(size)
    p = None

    try:
        p = PDFlib()

        p.set_option("searchpath={" + searchpath + "}")
        # p.set_option("license=w900201-010095-144031-B49YD2-9KN842")

        # This means we must check return values of load_font() etc.
        p.set_option("errorpolicy=return")

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
        p.set_info("Title", title)

        devicen = make_devicen(p, colors)

        # Loop over all pages of the input document
        for pageno in range(1, int(endpage)+1, 1):
            page = p.open_pdi_page(indoc, pageno, "cloneboxes")

            if page == -1:
                print("Error: " + p.get_errmsg())
                next
            # Start a new page
            if not pageopen:
                p.begin_page_ext(float(pagewidth), float(pageheight), "")
                pageopen = True
            y = float(pageheight)-float(y)
            p.fit_pdi_page(page, 0, pageheight, "cloneboxes")
            qcolors = len(colors)
            qint = len(intensities)
            retX = -1
            retY = -1
            if sideX == "i":
                if place == "T" or place == "B":
                    x = x-qcolors*qint*size
                elif place == "R" or place == "L":
                    x = x-size
                retX = x
            if sideY == "i":
                if place == "T" or place == "B":
                    y = y+size
                elif place == "L" or place == "R":
                    y = y+qcolors*qint*size
                retY = y
            for index, color in enumerate(colors, start=0):
                for i in intensities:
                    intense = int(i)/100
                    ceros = ""
                    for a in range(len(colors)):
                        if (a == index):
                            ceros = ceros + str(intense)+" "
                        else:
                            ceros = ceros + "0 "
                    p.set_graphics_option(
                        "fillcolor={ devicen " + str(devicen)+" " + ceros + "}")

                    if place == "L" or place == "R":
                        p.rect(x, y-size, size, size)
                        y = y-size
                    elif place == "T":
                        p.rect(x, y-size, size, size)
                        x = x+size
                    else:
                        p.rect(x, y-size, size, size)
                        x = x+size
                    p.fill()
            if place == "L" or place == "R":
                y = y+size
            else:
                x = x-size

            if sideX == "f":
                x = x+size
                retX = x

            if sideY == "f":
                y = y-size
                retY = y

            p.close_pdi_page(page)

            p.end_page_ext("")

        p.close_pdi_document(indoc)

        p.end_document("")
        return (json.dumps({
                "retX": retX,
                "retY": float(pageheight)-retY,
                }))
    except PDFlibException as ex:
        print("PDFlib exception occurred:")
        print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

    except Exception as ex:
        print(ex)

    finally:
        if p:
            p.delete()
