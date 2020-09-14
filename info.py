
import sys
import json
from PDFlib.PDFlib import *

def make(searchpath, pdffile, outfile, info, fsize,x,y,place,sideX,sideY):
    title = "Nombre de colores"
    fsize = float(fsize)
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

        endpage = p.pcos_get_number(indoc, "length:pages")
        pageopen = False 
        pagewidth=p.pcos_get_number(indoc, "pages[0]/width")
        pageheight=p.pcos_get_number(indoc, "pages[0]/height")
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
            y= float(pageheight)-float(y)
            if place=="L":
                angle=90
            elif place=="R":
                angle=270
            else:
                angle=0

            optlist = "fontname=Helvetica fontsize=" + str(fsize) + " encoding=unicode rotate=" + str(angle) + " fillcolor={ spotname All 1}"
            totalW = p.info_textline(info, "width", optlist)
            totalH = p.info_textline(info, "height", optlist)
            retX=-1
            retY=-1
            if sideX == "i":
                if place=="T" or place=="B":
                    x=x-totalW
                elif place=="R":
                    x=x-totalH
                    
                retX=x
            else:
                if place=="L":
                    x=x+totalH

            if sideY == "i":
                if place=="B":
                    y=y+totalH
                elif  place=="R":
                    y=y+totalW
                elif place=="L":
                    y=y+totalW
                retY=y
            else:
                if place=="T":
                    y=y-totalH
            
            if place=="L":
                if sideY == "i":
                    p.fit_textline(info, x, y-totalW, optlist)
                else:
                    p.fit_textline(info, x, y-totalW, optlist)
                    y=y-totalW
            elif place=="R":
                if sideY == "i":
                    p.fit_textline(info, x, y, optlist)
                    y=y+totalW
                else:
                    p.fit_textline(info, x, y, optlist)
                    y=y-totalW
            elif place=="T":
                if sideX == "i":  
                    p.fit_textline(info, x, y, optlist)
                    x=x-totalW
                else:  
                    p.fit_textline(info, x, y, optlist)
                    x=x+totalW
            else:
                if sideX == "i":
                    p.fit_textline(info, x, y-totalH, optlist)
                    x=x-totalW
                else:    
                    p.fit_textline(info, x, y-totalH, optlist)
                    x=x+totalW

            #p.fit_textline(info, x, y, optlist)
            if sideX == "f":
                retX=x 
            
            if sideY == "f":
                retY=y 
            
            

            p.close_pdi_page(page)
        
            p.end_page_ext("")

        p.close_pdi_document(indoc)
        
        
        p.end_document("")

        return (json.dumps({
                "retX":retX,
                "retY":float(pageheight)-retY,
            }))
    except PDFlibException as ex:
        print("PDFlib exception occurred:")
        print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

    except Exception as ex:
        print(ex)

    finally:
        if p:
            p.delete()
