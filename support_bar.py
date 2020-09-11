import sys
from PDFlib.PDFlib import *

def make(searchpath, pdffile, outfile, x, y, width, height,percent):
    title = "Barra de soporte"
    #searchpath = sys.argv[1]
    #pdffile = sys.argv[2]
    #outfile = sys.argv[3]
    #x = sys.argv[4]
    #y = sys.argv[5]
    #width = sys.argv[6]
    #height = sys.argv[7]
    percent=str(percent)
    p = None

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

            p.fit_pdi_page(page, 0, pageheight,"cloneboxes")
            p.set_graphics_option("fillcolor={spotname All "+percent+"} strokecolor={spotname All "+percent+"}");
            p.moveto(0, 0);
            p.rect(float(x), float(pageheight)-float(y), float(width), float(height));
            p.fill();

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
