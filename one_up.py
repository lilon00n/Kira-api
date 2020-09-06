
import sys
import json
from PDFlib.PDFlib import *

def make(searchpath, pdffile, outfile, boxes,colors,percentages,info):
    title = "Nombre de colores"
    p = None
    info= json.loads(info)
    boxes= json.loads(boxes)
    print(boxes)
    def draw_corner(p, x, y, crop_mark,weight):
        p.save()
        p.translate(x, y)
        p.draw_path(crop_mark, 0, 0, "fill stroke linewidth="+str(weight))
        p.restore()
    
    def draw_crop_marks(p,x_margin, y_margin, size, weight, dist_height, dist_width,width, height):
        p.set_graphics_option("linewidth="+str(weight)+" fillcolor={spotname All 1} strokecolor={spotname All 1}");

        #Top left
        crop_mark = -1;
        crop_mark = p.add_path_point(crop_mark, 0, int(dist_height), "move", "stroke nofill")
        crop_mark = p.add_path_point(crop_mark, 0, int(size + dist_height), "line", "")
        crop_mark = p.add_path_point(crop_mark, int(-dist_width), 0, "move", "stroke nofill")
        crop_mark = p.add_path_point(crop_mark, int(-size - dist_width), 0, "line", "")
        x = x_margin 
        y = y_margin
        draw_corner(p, x, y, crop_mark, weight)

        #Top right
        crop_mark = -1;
        crop_mark = p.add_path_point(crop_mark, 0, int(dist_height), "move", "stroke nofill")
        crop_mark = p.add_path_point(crop_mark, 0, int(size + dist_height), "line", "")
        crop_mark = p.add_path_point(crop_mark, int(dist_width), 0, "move", "stroke nofill")
        crop_mark = p.add_path_point(crop_mark, int(size + dist_width), 0, "line", "")
        x = x_margin + width
        y = y_margin 
        draw_corner(p, x, y, crop_mark, weight)


        #Bottom left
        crop_mark = -1;
        crop_mark = p.add_path_point(crop_mark, 0, int(-dist_height), "move", "stroke nofill")
        crop_mark = p.add_path_point(crop_mark, 0, int(-size - dist_height), "line", "")
        crop_mark = p.add_path_point(crop_mark, int(-dist_width), 0, "move", "stroke nofill")
        crop_mark = p.add_path_point(crop_mark, int(-size - dist_width), 0, "line", "")
        x = x_margin
        y = y_margin - height
        draw_corner(p, x, y, crop_mark, weight)


        #Bottom right
        crop_mark = -1;
        crop_mark = p.add_path_point(crop_mark, 0, int(-dist_height), "move", "stroke nofill strokecolor={gray 0}")
        crop_mark = p.add_path_point(crop_mark, 0, int(-size - dist_height), "line", "")
        crop_mark = p.add_path_point(crop_mark, int(dist_width), 0, "move", "stroke nofill strokecolor={gray 0}")
        crop_mark = p.add_path_point(crop_mark, int(size + dist_width), 0, "line", "")
        x = x_margin +width
        y = y_margin - height
        draw_corner(p, x, y, crop_mark, weight)
    try:
        p = PDFlib()

        searchnalapath = './data'
        p.set_option("searchpath={" + searchnalapath + "}")
        #Open the input PDF */
        nalapdf = p.open_pdi_document('nala-rotulo.pdf', "")
        if nalapdf == -1:
            print("Error: " + p.get_errmsg())
            next
        

        p.set_option("searchpath={" + searchpath + "}")
        #p.set_option("license=w900201-010093-143958-YCM672-UA9XC2")
        

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
        print(pagewidth)
        print(pageheight)
        if p.begin_document(outfile, "") == -1:
            raise "Error: " + p.get_errmsg()
        
        # Loop over all pages of the input document 
        
        page = p.open_pdi_page(indoc, 1, "pdiusebox=trim")
        if page == -1: 
            print("Error: " + p.get_errmsg())
            next
        nalapage = p.open_pdi_page(nalapdf, 1, "")
        if nalapage == -1: 
            print("Error: " + p.get_errmsg())
            next
        trimW=float(boxes["trimWidth"])*72/25.4
        trimH=float(boxes["trimHeight"])*72/25.4
        
        crop_size=5
        rotuloSize=80
        # Start a new page 
        if not pageopen: 
            p.begin_page_ext(trimW+crop_size*4*72/25.4, trimH+90, "trimbox={ "+str(crop_size*2*72/25.4)+" "+str(rotuloSize)+" "+str(trimW+crop_size*2*72/25.4)+ " "+ str(trimH+rotuloSize)+" } bleedbox={ 5 75 "+str(trimW+15)+ " "+ str(trimH+85)+" }")
            pageopen = True
        #unitario
        p.fit_pdi_page(page, crop_size*2*72/25.4, rotuloSize,"")
        #imagen nala
        p.fit_pdi_page(nalapage, crop_size*2*72/25.4, crop_size*2*72/25.4,"scale={0.6 0.6}")
        
        draw_crop_marks(p, 2*crop_size*72/25.4, trimH+rotuloSize, crop_size*72/25.4, 0.1, 0, 0,trimW ,trimH)

        p.set_graphics_option("strokecolor={ cmyk 0 0 0 1}")
        # Dibujo cotas
        #Superior
        p.moveto(2*crop_size*72/25.4, rotuloSize-3)
        p.lineto(trimW+2*crop_size*72/25.4, rotuloSize-3)
        p.stroke()
        #Inferior
        p.moveto(2*crop_size*72/25.4, rotuloSize+trimH+3)
        p.lineto(trimW+2*crop_size*72/25.4, rotuloSize+trimH+3)
        p.stroke()

        #Izquierda
        p.moveto(2*crop_size*72/25.4-3, rotuloSize)
        p.lineto(2*crop_size*72/25.4-3, rotuloSize+trimH)
        p.stroke()

        #Dereca
        p.moveto(2*crop_size*72/25.4+trimW+3, rotuloSize)
        p.lineto(2*crop_size*72/25.4+trimW+3, rotuloSize+trimH)
        p.stroke()

        xGen= 120;
        y=rotuloSize-crop_size*72/25.4-5
        size=7
        fsize=8
        # Dibujo colores
        for index, color in enumerate(colors, start=0):    
            if "PANTONE" in color:
                optlist = "fontname=Helvetica fontsize=" + str(fsize)+ " encoding=unicode fillcolor={ spotname { " + color  +"} 1}"
            else:
                optlist = "fontname=Helvetica fontsize=" + str(fsize)+ " encoding=unicode fillcolor={ " + color  +"}"

            textline = color;
            textwidth = p.info_textline(textline, "width", optlist);
            textheight = p.info_textline(textline, "height", optlist);

            p.fit_textline(textline, xGen-textwidth, y, optlist)

            p.fit_textline(percentages[index]+"%", xGen+20, y, optlist)
            
            if "PANTONE" in color:
                p.set_graphics_option("fillcolor={ spotname { " +color +  "} 1")
                p.rect(xGen+2, y+4, 7, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ spotname { " +color +  "} 1")
                p.rect(xGen+2, y+4, 7, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ spotname { " +color +  "} 1")
                p.rect(xGen+2+7, y+4, 7, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ spotname { " +color +  "} 1")
                p.rect(xGen+2+7, y+4, 7, 4)
                p.fill()

                p.set_graphics_option("strokecolor={ spotname { " +color +  "} 1")
            if color=="Cyan":
                p.set_graphics_option("fillcolor={ cmyk 1 0 0 0 }")
                p.rect(xGen+2, y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0.7 0 0 0 }")
                p.rect(xGen+2, y, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0.5 0 0 0 }")
                p.rect(xGen+2+int(size), y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0.2 0 0 0 }")
                p.rect(xGen+2+int(size), y, int(size), 4)
                p.fill()

                p.set_graphics_option("strokecolor={ cmyk 1 0 0 0 }")
            if color=="Magenta":
                p.set_graphics_option("fillcolor={ cmyk 0 1 0 0 }")
                p.rect(xGen+2, y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0.7 0 0 }")
                p.rect(xGen+2, y, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0.5 0 0 }")
                p.rect(xGen+2+int(size), y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0.2 0 0 }")
                p.rect(xGen+2+int(size), y, int(size), 4)
                p.fill()

                p.set_graphics_option("strokecolor={ cmyk 0 1 0 0 }")
            if color=="Yellow":
                p.set_graphics_option("fillcolor={ cmyk 0 0 1 0 }")
                p.rect(xGen+2, y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0.7 0 }")
                p.rect(xGen+2, y, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0.5 0 }")
                p.rect(xGen+2+int(size), y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0.2 0 }")
                p.rect(xGen+2+int(size), y, int(size), 4)
                p.fill()

                p.set_graphics_option("strokecolor={ cmyk 0 0 1 0 }")
            if color=="Black":
                p.set_graphics_option("fillcolor={ cmyk 0 0 0 1}")
                p.rect(xGen+2, y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0 0.7}")
                p.rect(xGen+2, y, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0 0.5}")
                p.rect(xGen+2+int(size), y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0 0.2}")
                p.rect(xGen+2+int(size), y, int(size), 4)
                p.fill()

                p.set_graphics_option("strokecolor={ cmyk 0 0 0 1}")
            if color=="Red":
                p.set_graphics_option("fillcolor={ rgb 1 0 0 }")
                p.rect(xGen+2, y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0.7 0 0 }")
                p.rect(xGen+2, y, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0.5 0 0 }")
                p.rect(xGen+2+int(size), y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0.2 0 0 }")
                p.rect(xGen+2+int(size), y, int(size), 4)
                p.fill()

                p.set_graphics_option("strokecolor={ rgb 1 0 0 }")
            if color=="Green":
                p.set_graphics_option("fillcolor={ rgb 0 1 0 }")
                p.rect(xGen+2, y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0.7 0 }")
                p.rect(xGen+2, y, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0.5 0 }")
                p.rect(xGen+2+int(size), y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0.2 0 }")
                p.rect(xGen+2+int(size), y, int(size), 4)
                p.fill()

                p.set_graphics_option("strokecolor={ rgb 0 1 0 }")
            if color=="Blue":
                p.set_graphics_option("fillcolor={ rgb 0 0 1 }")
                p.rect(xGen+2, y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0 0.7 }")
                p.rect(xGen+2, y, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0 0.5 }")
                p.rect(xGen+2+int(size), y+4, int(size), 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0 0.2 }")
                p.rect(xGen+2+int(size), y, int(size), 4)
                p.fill()

                p.set_graphics_option("strokecolor={ rgb 0 0 1 }")


            # Dibujo la linea separdora
            p.moveto(80, y-2)
            p.lineto(150,y-2)
            p.stroke()

            y=y-textheight-8


        #Escribo infos
        titles=["Cliente:", "Vendedor:", "Fecha de pedido:","Fecha de entrega:","Esp. técnica:","Archivo:", "Maquina:", "Material:"]
        keys=["customer", "salesman", "orderDate", "deliveryDate", "tsCode", "fileName", "machine", "material"]

        xGen= 250;
        y=rotuloSize-crop_size*72/25.4-5
        optlist = "fontname=Helvetica fontsize="+str(fsize)+" encoding=unicode fillcolor={ Black }"
        maxTextWidth=0
        for index, key in enumerate(keys, start=0):
            textline = titles[index];
            textwidth = p.info_textline(textline, "width", optlist);
            textheight = p.info_textline(textline, "height", optlist);
            p.fit_textline(textline, xGen-textwidth, y, optlist)

            p.set_graphics_option("strokecolor={ cmyk 0 0 0 1}")
            p.moveto(xGen-textwidth, y-2)
            p.lineto(xGen,y-2)
            p.stroke()
            textline = info[key];
            textwidth = p.info_textline(textline, "width", optlist);
            p.fit_textline(textline, xGen+2, y, optlist)

            if(textwidth >maxTextWidth):
                maxTextWidth=textwidth
            
            if index==3:
                y=rotuloSize-crop_size*72/25.4-5
                xGen= xGen+maxTextWidth+40
            else:
                y=y-textheight-4

        
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
