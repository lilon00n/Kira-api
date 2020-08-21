from PDFlib.PDFlib import *
import sys
import json
def make(searchpath, pdffile, outfile, colors, fsize,x,y,place,sideX,sideY):
    title = "Nombre de colores"
    #searchpath = sys.argv[1]
    #pdffile = sys.argv[2]
    #outfile = sys.argv[3]
    colorNames= colors
    
    colors = colors.split(',')
    fsize = float(fsize)
    x = float(x)
    y = float(y)
    #place = sys.argv[8]
    #sideX = sys.argv[9]
    #sideY = sys.argv[10]

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
        
        print("Aca1")
        # Loop over all pages of the input document 
        for pageno in range(1, int(endpage)+1, 1): 
            page = p.open_pdi_page(indoc, pageno, "")

            if page == -1: 
                print("Error: " + p.get_errmsg())
                next
            print("Aca2")
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

            retX=-1
            retY=-1
            optlist = "fontname=Helvetica fontsize=" + str(fsize)+ " encoding=unicode rotate="+ str(angle)
            totalW = p.info_textline(colorNames, "width", optlist)
            totalH = p.info_textline(colorNames, "height", optlist)
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
            for color in colors: 
                if "PANTONE" in color:
                    optlist = "fontname=Helvetica fontsize=" + str(fsize)+ " encoding=unicode rotate="+ str(angle) + " fillcolor={ spotname { " + color  +"} 1}"
                else:
                    optlist = "fontname=Helvetica fontsize=" + str(fsize)+ " encoding=unicode rotate="+ str(angle) + " fillcolor={ " + color  +"}"
                
                textline = color;
                textwidth = p.info_textline(textline, "width", optlist);
                textheight = p.info_textline(textline, "height", optlist);
                
                if place=="L":
                    if sideY == "i":
                        p.fit_textline(textline, x, y, optlist)
                        y=y-textwidth
                    else:
                        p.fit_textline(textline, x, y+textwidth, optlist)
                        y=y+textwidth
                elif place=="R":
                    if sideY == "i":
                        p.fit_textline(textline, x, y-textwidth, optlist)
                        y=y-textwidth
                    else:
                        p.fit_textline(textline, x, y, optlist)
                        y=y+textwidth
                elif place=="T":
                    if sideX == "i":  
                        p.fit_textline(textline, x-textwidth, y, optlist)
                        x=x-textwidth
                    else:  
                        p.fit_textline(textline, x, y, optlist)
                        x=x+textwidth
                else:
                    if sideX == "i":
                        p.fit_textline(textline, x-textwidth, y+textheight, optlist)
                        x=x-textwidth
                    else:    
                        p.fit_textline(textline, x, y+textheight, optlist)
                        x=x+textwidth
                        
                    
            if sideX == "f":
                retX=x 
            
            if sideY == "f":
                retY=y 
            
            #retX=x 
            #retY=y 

            p.fit_pdi_page(page, 0, pageheight,"")

            p.close_pdi_page(page)
        
            p.end_page_ext("")

        p.close_pdi_document(indoc)
        
        
        p.end_document("")
        
        return (json.dumps({
                "retX":retX,
                "retY":retY,
            }))
    except PDFlibException as ex:
        print("PDFlib exception occurred:")
        print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

    except Exception as ex:
        print(ex)

    finally:
        if p:
            p.delete()
