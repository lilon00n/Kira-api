
import sys
from PDFlib.PDFlib import *
from make_devicen import make_devicen
import json


def make(searchpath, pdffile, outfile, x, y, colors, place, sideX, sideY):
    title = outfile
    x = float(x)
    y = float(y)

    p = None

    def draw_circle(p, x, y):
        for i in range(1, 16, 1):
            p.arc(x, y, 0.1+0.6*i, 0, 360)
            p.stroke()

    try:
        p = PDFlib()
        print("1")
        p.set_option("searchpath={" + searchpath + "}")
        p.set_option("license=w900202-010598-802290-LJJBF2-BEC8G2")

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
            page = p.open_pdi_page(indoc, pageno, "")

            if page == -1:
                print("Error: " + p.get_errmsg())
                next

            # Start a new page
            if not pageopen:
                p.begin_page_ext(float(pagewidth), float(
                    pageheight), "topdown=true")
                pageopen = True

            # Open the input PDF */
            # p.set_option("searchpath={" + './data' + "}")
            # circlesDoc = p.open_pdi_document("circles.pdf", "")
            # if circlesDoc == -1:
            #     print("Error: " + p.get_errmsg())
            #     next
            # circles = p.open_pdi_page(circlesDoc, 1, "")
            # p.fit_pdi_page(circles, float(x), float(y), "")
            radius = 0.1+0.6*16

            if place == "TL" or place == "BL":
                x = x-radius
            else:
                x = x+radius

            if place == "TL" or place == "TR":
                y = y+radius
            else:
                y = y-radius

            for index, color in enumerate(colors, start=0):
                ceros = ""
                for a in range(len(colors)):
                    if (a == index):
                        ceros = ceros + "1 "
                    else:
                        ceros = ceros + "0 "
                p.set_graphics_option(
                    "strokecolor={ devicen " + str(devicen)+" " + ceros + "} linewidth=0.24")

                draw_circle(p, x, y)

                if place == "TL" or place == "TR":
                    y = y+(radius*2)
                else:
                    y = y-(radius*2)

                # if place == "L" or place == "R":
                #         p.rect(x, y-size, size, size)
                #         y = y-size
                #     elif place == "T":
                #         p.rect(x, y-size, size, size)
                #         x = x+size
                #     else:
                #         p.rect(x, y-size, size, size)
                #         x = x+size
                #     p.fill()

            if place == "TL" or place == "TR":
                retY = y+radius
            else:
                retY = y-radius

            retX = x+radius*2

            p.fit_pdi_page(page, 0, pageheight, "")

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
