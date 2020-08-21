
import sys
from PDFlib.PDFlib import *

def make(searchpath, pdffile, outfile, rombofile, x, y):
    title = "Barra de soporte"
    x = float(x)
    y = float(y)

    p = None

    try:
        p = PDFlib()

        p.set_option("searchpath={" + searchpath + "}")
        p.set_option("license=w900201-010093-143958-YCM672-UA9XC2")
        

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
            page = p.open_pdi_page(indoc, pageno, "")

            if page == -1: 
                print("Error: " + p.get_errmsg())
                next
            
            # Start a new page 
            if not pageopen: 
                p.begin_page_ext(float(pagewidth), float(pageheight), "topdown=true")
                pageopen = True

            #Open the input PDF */
            rombodoc = p.open_pdi_document(rombofile, "")
            if rombodoc == -1:
                print("Error: " + p.get_errmsg())
                next
            rombo = p.open_pdi_page(rombodoc, 1, "")
            p.fit_pdi_page(rombo, float(x), float(y),"")

            p.fit_pdi_page(page, 0, pageheight,"")

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
