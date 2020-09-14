import sys
from PDFlib.PDFlib import *
import json

def make(searchpath, pdffile, outfile, colors,intensities,size,x,y,place,sideX,sideY):
    title = "Nombre de colores"
    intensities=intensities.split(',')
    x = float(x)
    y = float(y)
    size = float(size)
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
            qcolors=len(colors)
            qint=len(intensities)
            retX=-1
            retY=-1
            if sideX == "i":
                if place=="T" or place=="B":
                    x=x-qcolors*qint*size
                elif place=="R" or place=="L" :
                    x=x-size
                retX=x

            if sideY == "i":
                if place=="T" or place=="B":
                    y=y+size
                elif place=="L" or place=="R":
                    y=y+qcolors*qint*size
                retY=y
            for color in colors: 
                for i in intensities: 
                    intense=int(i)/100
                    if "PANTONE" in color:
                        p.set_graphics_option("fillcolor={ spotname { " +color +  "} " + str(intense) +"}")
                    if color=="Cyan":
                        p.set_graphics_option("fillcolor={ cmyk " + str(intense) + " 0 0 0 }")
                    if color=="Magenta":
                        p.set_graphics_option("fillcolor={ cmyk 0 " + str(intense) + " 0 0 }")
                    if color=="Yellow":
                        p.set_graphics_option("fillcolor={ cmyk 0 0 " + str(intense) + " 0 }")
                    if color=="Black":
                        p.set_graphics_option("fillcolor={ cmyk 0 0 0 " + str(intense) + "}")
                    if color=="Red":
                        p.set_graphics_option("fillcolor={ rgb " + str(intense) + " 0 0 }")
                    if color=="Green":
                        p.set_graphics_option("fillcolor={ rgb 0 " + str(intense) + " 0 }")
                    if color=="Blue":
                        p.set_graphics_option("fillcolor={ rgb 0 0 " + str(intense) + " }")
                    
                    if place=="L" or place=="R":
                        p.rect(x, y-size, size, size)
                        y=y-size
                    elif place=="T":
                        p.rect(x, y-size, size, size)
                        x=x+size
                    else:
                        p.rect(x, y-size , size, size)
                        x=x+size
                    p.fill()
            if place=="L" or place=="R":
                y=y+size
            else:
                x=x-size
            
            if sideX == "f":
                x=x+size
                retX=x 
            
            if sideY == "f":
                y=y-size
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
