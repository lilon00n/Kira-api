title = "Nombre de colores"

import sys
searchpath = sys.argv[1]
pdffile = sys.argv[2]
outfile = sys.argv[3]
info = sys.argv[4]
fsize = float(sys.argv[5])
x = float(sys.argv[6])
y = float(sys.argv[7])
place = sys.argv[8]
sideX = sys.argv[9]
sideY = sys.argv[10]
from PDFlib.PDFlib import *

p = None

try:
    p = PDFlib()

    p.set_option("searchpath={" + searchpath + "}")

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
        page = p.open_pdi_page(indoc, pageno, "")

        if page == -1: 
            print("Error: " + p.get_errmsg())
            next
        
        # Start a new page 
        if not pageopen: 
            p.begin_page_ext(float(pagewidth), float(pageheight), "topdown=true")
            pageopen = True

        if place=="L":
            angle=90
        elif place=="R":
            angle=270
        else:
            angle=0

        optlist = "fontname=Helvetica fontsize=" + str(fsize) + " encoding=unicode rotate=" + str(angle) + " fillcolor={ spotname ALL 1}"
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
                y=y-totalH
            elif  place=="R":
                y=y-totalW
            elif place=="L":
                y=y-totalW
            retY=y
        else:
            if place=="T":
                y=y+totalH
        
        if place=="L":
            if sideY == "i":
                p.fit_textline(info, x, y, optlist)
                y=y-totalW
            else:
                p.fit_textline(info, x, y+totalW, optlist)
                y=y+totalW
        elif place=="R":
            if sideY == "i":
                p.fit_textline(info, x, y-totalW, optlist)
                y=y-totalW
            else:
                p.fit_textline(info, x, y, optlist)
                y=y+totalW
        elif place=="T":
            if sideX == "i":  
                p.fit_textline(info, x-totalW, y, optlist)
                x=x-totalW
            else:  
                p.fit_textline(info, x, y, optlist)
                x=x+totalW
        else:
            if sideX == "i":
                p.fit_textline(info, x-totalW, y+totalW, optlist)
                x=x-totalW
            else:    
                p.fit_textline(info, x, y+totalW, optlist)
                x=x+totalW

        #p.fit_textline(info, x, y, optlist)
        if sideX == "f":
            retX=x 
        
        if sideY == "f":
            retY=y 
        
        print(retX) 
        print(retY)

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
