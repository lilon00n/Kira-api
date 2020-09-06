import sys
import json
from PDFlib.PDFlib import *

def make(searchpath, pdffile, outfile, x, y, crop_size,weight):

    title = "Marcas de corte"
    #searchpath = sys.argv[1]
    #pdffile = sys.argv[2]
    #outfile = sys.argv[3]
    x = float(x)
    y = float(y)
    weight = str(weight)
    crop_size = float(crop_size)



    p = None

    def create_registration_mark(p, radius):
        registration_mark = -1
        #Long black lines
        for step in range(0, 2, 1):
            registration_mark = p.add_path_point(registration_mark,
                    radius, step * 90,
                    "move", "stroke nofill strokecolor={spotname All 1} polar")
            registration_mark = p.add_path_point(registration_mark,
                    radius, (step + 2) * 90, "line", "polar")
        

        #Inner circle
        registration_mark = p.add_path_point(registration_mark,
                -radius / 3, 0, "move",
                "fill nostroke strokecolor={spotname All 1} fillcolor={spotname All 1}")
        registration_mark = p.add_path_point(registration_mark,
                radius / 3, 0, "control", "")
        registration_mark = p.add_path_point(registration_mark,
                -radius / 3, 0, "circular", "")

        #Short white lines
        for  step in range(0, 2, 1):
            registration_mark = p.add_path_point(registration_mark, radius / 3, step * 90,
                    "move", "stroke nofill strokecolor={gray 1} polar")
            registration_mark = p.add_path_point(registration_mark,
                    radius / 3, (step + 2) * 90, "line", "polar")
        
        #Outer circle
        registration_mark = p.add_path_point(registration_mark, -2
                * radius / 3, 0, "move",
                "stroke nofill strokecolor={spotname All 1}")
        registration_mark = p.add_path_point(registration_mark,
                2 * radius / 3, 0, "control", "")
        registration_mark = p.add_path_point(registration_mark, -2
                * radius / 3, 0, "circular", "")
        
        return registration_mark

    def draw_corner(p, angle, x, y, crop_mark):
        p.save()
        p.translate(x, y)
        p.rotate(angle)
        p.draw_path(crop_mark, 0, 0, "fill stroke")
        p.restore()


    try:
        p = PDFlib()

        p.set_option("searchpath={" + searchpath + "}")
        #p.set_option("license=w900201-010093-143958-YCM672-UA9XC2")
        
        # This means we must check return values of load_font() etc. 
        p.set_option("errorpolicy=return")

        #Open the input PDF */
        indoc = p.open_pdi_document(pdffile, "")
        if indoc == -1:
            print("Error: " + p.get_errmsg())
            next
        pagewidth=p.pcos_get_number(indoc, "pages[0]/width")
        pageheight=p.pcos_get_number(indoc, "pages[0]/height")

        endpage = p.pcos_get_number(indoc, "length:pages")
        pageopen = False 

        if p.begin_document(outfile, "") == -1:
            raise "Error: " + p.get_errmsg()

        p.set_info("Creator", "PDFlib Cookbook")
        p.set_info("Title", title )
        
        
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

            y= float(pageheight)-float(y)
            p.fit_pdi_page(page, 0, pageheight,"cloneboxes")

            p.set_graphics_option("fillcolor={spotname All 0.5} strokecolor={spotname All 0.5} linewidth="+weight)
            registration_mark = create_registration_mark(p, int(crop_size))
            draw_corner(p, 0, x, y,  registration_mark)
            
            

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

