import os
ENV = os.getenv("ENV")
#outfile = "crop_mark.pdf"
#pdffile = "/Users/aldanaveronruizdiaz/Documents/Proyectos/nala/p-server/api/pdflib/data/00000400_layout.pdf"
import sys
import json
from PDFlib.PDFlib import *
from make_devicen import make_devicen


def make(searchpath, pdffile, outfile, colors, x_margin, y_margin, size, width, height, dist_width, dist_height, weight):
    paths = outfile.split("\\")
    if len(paths) == 1:
        paths = outfile.split("/")
    title = paths[len(paths)-1]
    #searchpath = sys.argv[1]
    #pdffile = sys.argv[2]
    #outfile = sys.argv[3]
    x_margin = float(x_margin)
    y_margin = float(y_margin)
    size = float(size)
    width = float(width)
    height = float(height)
    weight = str(weight)
    dist_width = float(dist_width)
    dist_height = float(dist_height)

    print(x_margin)
    print(y_margin)
    print(size)
    print(width)
    print(height)
    print(weight)
    print(dist_width)
    print(dist_height)

    p = None

    def draw_corner(p, x, y, crop_mark):
        p.save()
        p.translate(x, y)
        p.draw_path(crop_mark, 0, 0, "fill stroke linewidth="+weight)
        p.restore()

    try:
        p = PDFlib()

        p.set_option("searchpath={" + searchpath + "}")
        if ENV == "development":
            print("we are in development mode. do not worry about license")
        elif ENV == "production":
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
            page = p.open_pdi_page(indoc, pageno, "cloneboxes")

            if page == -1:
                print("Error: " + p.get_errmsg())
                next

            # Start a new page
            if not pageopen:
                p.begin_page_ext(float(pagewidth), float(pageheight), "")
                pageopen = True
            y_margin = float(pageheight)-float(y_margin)
            p.fit_pdi_page(page, 0, pageheight, "cloneboxes")

            ones = ""
            for a in range(len(colors)):
                ones = ones + "1 "

            p.set_graphics_option("fillcolor={devicen " + str(devicen)+" " + ones +
                                  "} strokecolor={devicen " + str(devicen)+" " + ones + "} linewidth="+weight)

            # Top left
            crop_mark = -1
            crop_mark = p.add_path_point(crop_mark, 0, int(
                dist_height), "move", "stroke nofill")
            crop_mark = p.add_path_point(
                crop_mark, 0, int(size + dist_height), "line", "")
            crop_mark = p.add_path_point(
                crop_mark, int(-dist_width), 0, "move", "stroke nofill")
            crop_mark = p.add_path_point(
                crop_mark, int(-size - dist_width), 0, "line", "")
            x = x_margin
            y = y_margin
            draw_corner(p, x, y, crop_mark)

            # Top right
            crop_mark = -1
            crop_mark = p.add_path_point(crop_mark, 0, int(
                dist_height), "move", "stroke nofill")
            crop_mark = p.add_path_point(
                crop_mark, 0, int(size + dist_height), "line", "")
            crop_mark = p.add_path_point(crop_mark, int(
                dist_width), 0, "move", "stroke nofill")
            crop_mark = p.add_path_point(
                crop_mark, int(size + dist_width), 0, "line", "")
            x = x_margin + width
            y = y_margin
            draw_corner(p, x, y, crop_mark)

            # Bottom left
            crop_mark = -1
            crop_mark = p.add_path_point(
                crop_mark, 0, int(-dist_height), "move", "stroke nofill")
            crop_mark = p.add_path_point(
                crop_mark, 0, int(-size - dist_height), "line", "")
            crop_mark = p.add_path_point(
                crop_mark, int(-dist_width), 0, "move", "stroke nofill")
            crop_mark = p.add_path_point(
                crop_mark, int(-size - dist_width), 0, "line", "")
            x = x_margin
            y = y_margin - height
            draw_corner(p, x, y, crop_mark)

            # Bottom right
            crop_mark = -1
            crop_mark = p.add_path_point(
                crop_mark, 0, int(-dist_height), "move", "stroke nofill strokecolor={gray 0}")
            crop_mark = p.add_path_point(
                crop_mark, 0, int(-size - dist_height), "line", "")
            crop_mark = p.add_path_point(crop_mark, int(
                dist_width), 0, "move", "stroke nofill strokecolor={gray 0}")
            crop_mark = p.add_path_point(
                crop_mark, int(size + dist_width), 0, "line", "")
            x = x_margin + width
            y = y_margin - height
            draw_corner(p, x, y, crop_mark)

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
