import sys
import json
from PDFlib.PDFlib import *


def make(searchpath, pdffile, outfile, x, y, crop_size):
    title = "Marcas de corte"

    x = float(x)
    y = float(y)
    crop_size = float(crop_size)

    p = None

    def create_micropoint(p, radius):
        micropoint = -1

        # Outer circle
        micropoint = p.add_path_point(micropoint, - radius / 0.3514729,
                                      0, "move",  "linewidth=0.01 fill nostroke fillcolor={gray 1}")
        micropoint = p.add_path_point(
            micropoint,   radius / 0.3514729, 0, "control", "")
        micropoint = p.add_path_point(
            micropoint, - radius / 0.3514729, 0, "circular", "")

        # Inner circle
        micropoint = p.add_path_point(micropoint, -(radius/2) / 0.3514729, 0, "move",
                                      "fill nostroke strokecolor={spotname All 0.5} fillcolor={spotname All 0.5}")
        micropoint = p.add_path_point(
            micropoint, (radius/2) / 0.3514729, 0, "control", "")
        micropoint = p.add_path_point(
            micropoint, -(radius/2) / 0.3514729, 0, "circular", "")

        return micropoint

    def draw_corner(p, angle, x, y, crop_mark):
        p.save()
        p.translate(x, y)
        p.rotate(angle)
        p.draw_path(crop_mark, 0, 0, "fill stroke")
        p.restore()

    try:
        p = PDFlib()

        p.set_option("searchpath={" + searchpath + "}")
        p.set_option("license=w900201-010093-143958-YCM672-UA9XC2")

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

        p.set_info("Creator", "PDFlib Cookbook")
        p.set_info("Title", title)

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

            p.fit_pdi_page(page, 0, pageheight, "cloneboxes")
            y = float(pageheight)-float(y)
            p.set_graphics_option(
                "fillcolor={spotname All 0.5} strokecolor={spotname All 0.5}")
            micropoint = create_micropoint(p, crop_size)
            draw_corner(p, 0, x, y,  micropoint)

            p.close_pdi_page(page)

            p.end_page_ext("")

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
