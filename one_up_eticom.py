
import sys
import json
from PDFlib.PDFlib import *
from make_devicen import make_devicen
from clients import findClient


def make(searchpath, pdffile, planefile, outfile, client, boxes, colorsJson, info):
    client = findClient(client)
    paths = outfile.split("\\")
    if len(paths) == 1:
        paths = outfile.split("/")
    title = paths[len(paths)-1]
    p = None
    info = json.loads(info)
    print(info)
    boxes = json.loads(boxes)

    def draw_corner( x, y, crop_mark, weight):
        p.save()
        p.translate(x, y)
        p.draw_path(crop_mark, 0, 0, "fill stroke linewidth="+str(weight))
        p.restore()

    def draw_crop_marks( x_margin, y_margin, size, weight, dist_height, dist_width, width, height):
        p.set_graphics_option("linewidth="+str(weight))

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
        draw_corner( x, y, crop_mark, weight)

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
        draw_corner(x, y, crop_mark, weight)

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
        draw_corner( x, y, crop_mark, weight)

        # Bottom right
        crop_mark = -1
        crop_mark = p.add_path_point(
            crop_mark, 0, int(-dist_height), "move", "stroke nofill")
        crop_mark = p.add_path_point(
            crop_mark, 0, int(-size - dist_height), "line", "")
        crop_mark = p.add_path_point(crop_mark, int(
            dist_width), 0, "move", "stroke nofill")
        crop_mark = p.add_path_point(
            crop_mark, int(size + dist_width), 0, "line", "")
        x = x_margin + width
        y = y_margin - height
        draw_corner(x, y, crop_mark, weight)

    def create_registration_mark(radius):
        registration_mark = -1
        # Long black lines
        for step in range(0, 2, 1):
            registration_mark = p.add_path_point(registration_mark,
                                                 radius, step * 90,
                                                 "move", "stroke nofill  polar")
            registration_mark = p.add_path_point(registration_mark,
                                                 radius, (step + 2) * 90, "line", "polar")

        # Inner circle
        registration_mark = p.add_path_point(registration_mark,
                                             -radius / 3, 0, "move",
                                             "fill nostroke ")
        registration_mark = p.add_path_point(registration_mark,
                                             radius / 3, 0, "control", "")
        registration_mark = p.add_path_point(registration_mark,
                                             -radius / 3, 0, "circular", "")

        # Short white lines
        for step in range(0, 2, 1):
            registration_mark = p.add_path_point(registration_mark, radius / 3, step * 90,
                                                 "move", "stroke nofill strokecolor={gray 1} polar")
            registration_mark = p.add_path_point(registration_mark,
                                                 radius / 3, (step + 2) * 90, "line", "polar")

        # Outer circle
        registration_mark = p.add_path_point(registration_mark, -2
                                             * radius / 3, 0, "move",
                                             "stroke nofill ")
        registration_mark = p.add_path_point(registration_mark,
                                             2 * radius / 3, 0, "control", "")
        registration_mark = p.add_path_point(registration_mark, -2
                                             * radius / 3, 0, "circular", "")

        return registration_mark

    def draw_registration_mark(x, y, crop_mark):
        p.save()
        p.translate(x, y)
        p.draw_path(crop_mark, 0, 0, "fill stroke")
        p.restore()

    def fitAndGetWidth(text,xGen, y, endX, format):
        optlist = "fontname=Arial fontsize=" + str(12) + " encoding=unicode"
        if format==1:
            optlist+=" strokewidth=0.5 textrendering=2 strokecolor={ gray 0.3  } fillcolor={ gray 0.3 }"
            p.fit_textline(text, xGen, y, optlist)
        
        if format==2:
            optlist+=" boxsize={"+str(endX-5-xGen)+" "+ str(rowHeight)+ "} fitmethod=auto strokewidth=0.8 textrendering=2 strokecolor={ gray 0  } fillcolor={ gray 0 }"
            p.fit_textline(text, xGen, y, optlist)
        textWidth = p.info_textline(text, "width", optlist)
        return textWidth

    def drawFirstColumn( xGen,y):
        p.set_graphics_option(
            "strokecolor={ cmyk 0 1 0.88 0} fillcolor={ cmyk 0 1 0.88 0}")
        p.rect(xGen+columnWidth-5,y-rotuloHeight,  5, rotuloHeight)
        p.fill()

        y=y-rowHeight*2
        p.set_graphics_option(
            "strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")
        width = fitAndGetWidth("FECHA:", xGen, y,xGen+columnWidth/2,1)
        fitAndGetWidth("la de hoy", xGen+width+5, y, xGen+columnWidth/2, 2)
        width = fitAndGetWidth("CONSECUTIVO:", xGen+columnWidth/2, y, xGen+columnWidth, 1)
        fitAndGetWidth(info["tsCode"], xGen+columnWidth/2+width+5, y, xGen+columnWidth, 2)

        y=y-rowHeight
        width = fitAndGetWidth("No DE CLIENTE:", xGen, y,xGen+columnWidth/2,1)
        fitAndGetWidth(info["clientNumber"], xGen+width+5, y,xGen+columnWidth/2,2)
        width =fitAndGetWidth("COD CLIENTE:", xGen+columnWidth/2, y,xGen+columnWidth,1)
        fitAndGetWidth(info["customerCode"], xGen+columnWidth/2+width+5, y,xGen+columnWidth,2)
        y=y-rowHeight
        
        width =fitAndGetWidth("CLIENTE:", xGen, y,xGen+columnWidth,1)
        fitAndGetWidth(info["customer"], xGen+width+5, y,xGen+columnWidth,2)
        y=y-rowHeight
        
        width =fitAndGetWidth("TIPO PRODUCTO:", xGen, y,xGen+columnWidth,1)
        fitAndGetWidth(info["productType"], xGen+width+5, y,xGen+columnWidth,2)
        y=y-rowHeight

        width =fitAndGetWidth("PRODUCTO:", xGen, y,xGen+columnWidth,1)
        fitAndGetWidth(info["description"], xGen+width+5, y,xGen+columnWidth,2)
        y=y-rowHeight

        width =fitAndGetWidth("TIPO DE CODIGO:", xGen, y,xGen+columnWidth/2,1)
        fitAndGetWidth(info["barcodeType"], xGen+width+5, y,xGen+columnWidth/2,2)
        width =fitAndGetWidth("No. BARRAS:", xGen+columnWidth/2, y,xGen+columnWidth,1)
        fitAndGetWidth(info["barcodeNumber"], xGen+columnWidth/2+width+5, y,xGen+columnWidth,2)

        y=y-rowHeight
        width =fitAndGetWidth("DISEÑADOR:", xGen, y,xGen+columnWidth/2,1)
        fitAndGetWidth(info["designer"], xGen+width+5, y,xGen+columnWidth/2,2)
        width =fitAndGetWidth("REVISIÓN:", xGen+columnWidth/2, y,xGen+columnWidth,1)
        y=y-rowHeight
        
    def drawSecondColumn(xGen,y):  
        p.set_graphics_option(
            "strokecolor={ cmyk 0 1 0.88 0} fillcolor={ cmyk 0 1 0.88 0}")
        p.rect(xGen+columnWidth,y-rotuloHeight,  5, rotuloHeight)
        p.fill()

        y=y-rowHeight*2
        x=xGen+10
        optlist = "fontname=Arial fontsize=" + str(fsize) + " encoding=unicode"
        p.set_graphics_option(
            "strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")
        width=fitAndGetWidth("MEDIDA AL EJE EXTENDIDA:", x, y,x+columnWidth,1)
        fitAndGetWidth(boxes["trimWidth"] + " mm", x+width+5, y,x+columnWidth,2)
        y=y-rowHeight

        width=fitAndGetWidth("MEDIDA AL DESARROLLO EXTENDIDA:", x, y,x+columnWidth,1)
        fitAndGetWidth(boxes["trimHeight"] + " mm", x+width+5, y,x+columnWidth,2)
        y=y-rowHeight

        width=fitAndGetWidth("LINEA DE SUAJE:", x, y,x+columnWidth,1)
        y=y-rowHeight

        y=y-rowHeight
        width=fitAndGetWidth("ANCHO", x, y,x+columnWidth/4,1)
        fitAndGetWidth(str(info["planeWidth"]) + " mm", x, y+rowHeight,x+columnWidth/4,2)
        fitAndGetWidth("X", x+columnWidth/4-15, y+rowHeight,x+columnWidth/4,1)

        width=fitAndGetWidth("ALTO", x+columnWidth/4, y,x+columnWidth/4*2,1)
        fitAndGetWidth(str(info["planeHeight"]) + " mm", x+columnWidth/4, y+rowHeight,x+columnWidth/4*2,2)
        fitAndGetWidth("X", x+columnWidth/4*2-15, y+rowHeight, x+columnWidth/4*2,1)
        
        width=fitAndGetWidth("FUELLE", x+columnWidth/4*2, y, x+columnWidth/4*3,1)
        fitAndGetWidth(str(info["planeBellows"]) + " mm", x+columnWidth/4*2, y+rowHeight, x+columnWidth/4*3,2)
        fitAndGetWidth("X", x+columnWidth/4*3-15, y+rowHeight, x+columnWidth/4*3,1)
         
        width=fitAndGetWidth("TRASLAPE", x+columnWidth/4*3, y, x+columnWidth,1)
        fitAndGetWidth(str(info["planeOverlap"]) + " mm", x+columnWidth/4*3, y+rowHeight,x+columnWidth,2)
        
        y=y-rowHeight*2
    
    def drawThirdColumn(xGen, y):
        optlist = "fontname=Arial fontsize=" + str(17) + " encoding=unicode"
        tintasHeight = p.info_textline("TINTAS:", "height", optlist)
        tintasWidth = p.info_textline("TINTAS:", "width", optlist)
        cantHeight = p.info_textline("04", "height",  "fontname=Arial fontsize=" + str(20) + " encoding=unicode")
        cantWidth = p.info_textline("04", "width",  "fontname=Arial fontsize=" + str(20) + " encoding=unicode")


        p.set_graphics_option(
            "strokecolor={ cmyk 0 1 0.88 0} fillcolor={ cmyk 0 1 0.88 0}")
        p.rect(xGen+columnWidth-5,y-rotuloHeight,  5, rotuloHeight-tintasHeight*5)
        p.fill()

        x=xGen+10

        p.set_graphics_option(
            "strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")
        y=y-tintasHeight-5
        p.fit_textline("TINTAS:", x, y-tintasHeight, optlist+" strokewidth=0.5 textrendering=2 strokecolor={ gray 0.3  } fillcolor={ gray 0.3 }")
        y=y-tintasHeight-10
        optlist = "fontname=Arial fontsize=" + str(20) + " encoding=unicode"
        p.fit_textline("0"+str(len(colorsJson)), x+tintasWidth/2-cantWidth/2, y-cantHeight, optlist+" strokewidth=0.8 textrendering=2 strokecolor={ gray 0  } fillcolor={ gray 0 }")


        startedY=y-cantHeight

        p.set_option("searchpath={" + searchnalapath + "}")
        lineasSuaje = p.load_image("png", "detalle suaje_linea_sp.png", "page=1")
        if lineasSuaje == -1:
            print("Error: " + p.get_errmsg())
            next
    
        # logo cliente
        p.fit_image(lineasSuaje, xGen,
                   mediaExcess+cropExcess+2, " boxsize={ "+str(columnWidth) + " "+ str(startedY-15-(mediaExcess+cropExcess+2))+" } fitmethod=meet ")
        p.close_image(lineasSuaje)

        x=xGen+tintasWidth+10
        # Dibujo colores
        for index, color in enumerate(colorsJson, start=0):
            ceros = ""
            for xi in range(len(colorsJson)):
                if (xi == index):
                    ceros = ceros + "1 "
                else:
                    ceros = ceros + "0 "
            optlist = "fontname=Arial fontsize=" + \
                str(fsize) + \
                " encoding=unicode fillcolor={devicen " + \
                str(devicen)+" " + ceros + "}"
            textline = color["name"]
            textwidth = p.info_textline(textline, "width", optlist)
            textheight= p.info_textline(textline, "height", optlist)

            # p.fit_textline(textline, x-textwidth, y, optlist)

            # p.fit_textline(color["inkCov"]+"%", x+20, y, optlist)
            p.set_graphics_option(
                "fillcolor={ devicen " + str(devicen)+" " + ceros + "}")
            p.rect(x+2, y+4, colorSize, colorSize) 
            p.fill()
            p.fit_textline(textline, x+2, y-textheight, optlist)

            p.fit_textline(color["inkCov"]+"%", x+2, y-5-textheight*2, optlist)
            

            p.set_graphics_option(
                "strokecolor={ devicen " + str(devicen)+" " + ceros + "}")

            # # Dibujo la linea separdora
            # p.moveto(2*crop_size*72/25.4 + maxLogo, y-2)
            # p.lineto(x + colorSize*2+percentageWidth, y-2)
            # p.stroke()

            # y = y-textHeight-8

            x=x+textwidth+20
        
        

        return startedY

    def drawFourthColumn(xGen, y):
        p.set_graphics_option(
            "strokecolor={ cmyk 0 1 0.88 0} fillcolor={ cmyk 0 1 0.88 0}")
        p.rect(xGen+columnWidth-5,mediaExcess+cropExcess,  5, rotuloHeight)
        p.fill()

        optlist = "fontname=Arial fontsize=" + str(fsize) + " encoding=unicode"
        y=y-rowHeight*2
        p.set_graphics_option(
            "strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")

        x=xGen+10

        width=fitAndGetWidth("FORMATO DE ENTREGA:", x, y,x+columnWidth,1)
        fitAndGetWidth(info["deliverable"], x+width+5, y,x+columnWidth,2)
        y=y-rowHeight

        salida = info["salida"]+'.png'
        #Escribo salida 
        if info["salida"] != '':
            fitAndGetWidth("SALIDA:", x, y,x+columnWidth,1)
            searchnalapath = './data/embobinado'
            p.set_option("searchpath={" + searchnalapath + "}")
            imgSalida = p.load_image('png',salida, "page=1")
            imgSalidaHeight = p.info_image(
            imgSalida, "height", "scale=0.3")
            if imgSalida == -1:
                print("Error: " + p.get_errmsg())
                next
            p.fit_image(imgSalida, x,y-textHeight-imgSalidaHeight-4, "scale=0.3")
        

    def drawLastColumn(xGen, y):
        p.set_option("searchpath={" + searchnalapath + "}")
        terminos = p.load_image("png", "terminos_sp.png", "page=1")
        if terminos == -1:
            print("Error: " + p.get_errmsg())
            next
    
        # logo cliente
        p.fit_image(terminos, xGen,
                   mediaExcess+cropExcess+2, " boxsize={ "+str(columnWidth) + " "+ str(rotuloHeight)+" } fitmethod=meet ")
        p.close_image(terminos)

    def drawLogoColumn(x, y):
        p.set_graphics_option(
            "strokecolor={ cmyk 0 1 0.88 0} fillcolor={ cmyk 0 1 0.88 0}")
        p.rect(x,y-rotuloHeight, columnWidth-5, rotuloHeight)
        p.fill()
        p.set_option("searchpath={" + searchnalapath + "}")
        logoClient = p.load_image(client.ext, client.logo, "page=1")
        if logoClient == -1:
            print("Error: " + p.get_errmsg())
            next
    
        # logo cliente
        logoClientHeight = p.info_image(
            logoClient, "height", "scale=1.2")
        p.fit_image(logoClient, x+15,
                    y-logoClientHeight -15, "scale=1.2 ")
        p.close_image(logoClient)

        p.set_graphics_option(
            "strokecolor={ gray 1  } fillcolor={ gray 1 }")
        optlist = "fontname=Arial fontsize=" + str(25) + " encoding=unicode strokewidth=0.8 textrendering=2 "
        p.fit_textline("ESPECIFICACIONES",x+15,
                    y-logoClientHeight -50, optlist) 
        p.fit_textline("INGENIERÍA Y DISEÑO",x+15,
                    y-logoClientHeight -90, optlist)
    
    
    try:
        p = PDFlib()

        p.set_option("searchpath={" + searchpath + "}")
        searchnalapath = './data'
        #p.set_option("license=w900202-010598-802290-LJJBF2-BEC8G2")

        # This means we must check return values of load_font() etc.
        p.set_option("errorpolicy=return")
        # Open the input PDF */
        unitario = p.open_pdi_document(pdffile, "")
        if unitario == -1:
            print("Error: " + p.get_errmsg())
            next
        if info["oneUpType"] != 'none':
            plano = p.open_pdi_document(planefile, "")
            if plano == -1:
                print("Error: " + p.get_errmsg())
                next

        pageopen = False
        pagewidth = p.pcos_get_number(unitario, "pages[0]/width")
        pageheight = p.pcos_get_number(unitario, "pages[0]/height")
        if p.begin_document(outfile, "") == -1:
            raise "Error: " + p.get_errmsg()

        # Loop over all pages of the input document

        page = p.open_pdi_page(unitario, 1, "pdiusebox=bleed")
        if page == -1:
            print("Error: " + p.get_errmsg())
            next
        if info["oneUpType"] != 'none':
            planePage = p.open_pdi_page(plano, 1, "pdiusebox=bleed")
            if planePage == -1:
                print("Error: " + p.get_errmsg())
                next
        # nalapage = p.open_pdi_page(nalapdf, 1, "")
        # if nalapage == -1:
        #     print("Error: " + p.get_errmsg())
        #     next
        # p.set_option("searchpath={" + searchnalapath + "}")
        

        bleed0 = float(boxes["bleed"][0])
        bleed1 = float(boxes["bleed"][1])
        trim0 = float(boxes["trim"][0])
        trim1 = float(boxes["trim"][1])
        despX = bleed0-trim0
        despY = bleed1-trim1

        trimW = float(boxes["trimWidth"])*72/25.4
        trimH = float(boxes["trimHeight"])*72/25.4
        # nalaheight = p.pcos_get_number(nalapdf, "pages[0]/height")*0.6
        # nalawidth = p.pcos_get_number(nalapdf, "pages[0]/width")*0.6


        crop_size = 8
        colorSize = 26
        fsize = 8
        separation = 4
        cotaSeparation = 5*72/25.4  # 12mm del trim,
        cruzSeparation = 3*72/25.4  # 12mm del trim,
        bleedExcess = 5*72/25.4  # 5mm
        cropExcess = crop_size*72/25.4  # 8mm
        mediaExcess = 5*72/25.4  # 5mm
        materialMachines = info["materialMachines"]
        devicen = make_devicen(p, colorsJson)

        # Defino alto del rotulo
        optlist = "fontname=Arial fontsize=" + str(fsize) + " encoding=unicode"
        textHeight = p.info_textline("Un color", "height", optlist)

        rotuloHeight = 232

        # Defino ancho del rotulo
        # Chequeo donde comenzar a escribir los colores

        
        addInfo = 0
        if 1840 > trimW:
            addInfo = (1840-trimW)/2
        columnWidth= 325
        rowHeight = 23
        widths = []
        widths.append(columnWidth*6)
        widths.append(trimW)

        rotuloWidth= max(widths)
        

        trimbox = "{ "+str(mediaExcess+cropExcess+addInfo)+" "+str(mediaExcess+rotuloHeight+50+cropExcess)+" "+str(
            mediaExcess+cropExcess+addInfo+trimW) + " "+str(mediaExcess+rotuloHeight+50+cropExcess+trimH)+" }"
        bleedbox = "{ "+str(mediaExcess+cropExcess+addInfo-bleedExcess)+" "+str(mediaExcess+rotuloHeight+50+cropExcess-bleedExcess)+" "+str(
            mediaExcess+cropExcess+trimW+addInfo+bleedExcess) + " "+str(mediaExcess+rotuloHeight+50+cropExcess+trimH+bleedExcess)+" }"
        cropbox = "{ "+str(mediaExcess)+" "+str(mediaExcess)+" "+str(mediaExcess+cropExcess *
                                                                     2+rotuloWidth) + " "+str(mediaExcess+rotuloHeight+50+cropExcess*2+trimH)+" }"

        mediaWidth = rotuloWidth+cropExcess*2+mediaExcess*2
        mediaHeigth = trimH+cropExcess*2+mediaExcess*2+rotuloHeight+50

        # Start a new page
        if not pageopen:
            p.begin_page_ext(mediaWidth, mediaHeigth, "trimbox=" +
                             trimbox+" bleedbox="+bleedbox+" cropbox="+cropbox)
            pageopen = True

        # unitario
        p.fit_pdi_page(page, mediaExcess+cropExcess+addInfo+despX,
                       mediaExcess+rotuloHeight+50+cropExcess+despY, "")

        # plano
        p.fit_pdi_page(planePage, mediaExcess+cropExcess+addInfo+despX,
                       mediaExcess+rotuloHeight+50+cropExcess+despY, "")
        # nala
        # p.fit_pdi_page(nalapage, mediaExcess+cropExcess,
        #                mediaExcess+rotuloHeight-nalaheight, "scale={0.6 0.6}")
        # p.close_pdi_page(nalapage)
        # p.close_pdi_document(nalapdf)


        # Dibujo cruces de regisro
        ones = ""
        for x in range(len(colorsJson)):
            ones = ones + "1 "

        p.set_graphics_option("fillcolor={devicen " + str(devicen)+" " + ones +
                              "} strokecolor={devicen " + str(devicen)+" " + ones + "} linewidth=0.01")

        # Dibujo marcas de corte
        draw_crop_marks(mediaExcess+cropExcess+addInfo,  mediaExcess+rotuloHeight+50 +
                        cropExcess+trimH, crop_size*72/25.4, 0.01, 0, 0, trimW, trimH)

        medX = mediaExcess+cropExcess+addInfo+trimW/2
        medY = mediaExcess+rotuloHeight+50+cropExcess+trimH/2

        textCotaW = str(round(float(boxes["trimWidth"]), 3))+"mm"
        textCotaH = str(round(float(boxes["trimHeight"]), 3))+"mm"

        wCotaWidth = p.info_textline(textCotaW, "width", optlist)
        hCotaWidth = p.info_textline(textCotaW, "width", optlist+" rotate=90")
        hCotaHeight = p.info_textline(
            textCotaW, "height", optlist+" rotate=90")

        registration_mark = create_registration_mark( 5)
        draw_registration_mark( medX, mediaExcess+rotuloHeight+50+cropExcess +
                               trimH+separation+hCotaHeight/2+cruzSeparation,  registration_mark)  # Top
        draw_registration_mark( medX, mediaExcess+rotuloHeight+50+cropExcess -
                               separation-hCotaHeight/2-cruzSeparation,  registration_mark)  # Bottom
        draw_registration_mark( mediaExcess+cropExcess+addInfo -
                               separation-hCotaHeight/2-cruzSeparation, medY,  registration_mark)  # Left
        draw_registration_mark( mediaExcess+cropExcess+addInfo+trimW +
                               separation+hCotaHeight/2+cruzSeparation, medY,  registration_mark)  # Right

        p.set_graphics_option("strokecolor={ cmyk 0 0 0 1}")

        # Dibujo cotas
        # Superior
        p.moveto(mediaExcess+cropExcess+addInfo, mediaExcess +
                 rotuloHeight+50+cropExcess+trimH+cotaSeparation)
        p.lineto(mediaExcess+cropExcess+addInfo+trimW, mediaExcess +
                 rotuloHeight+50+cropExcess+trimH+cotaSeparation)
        p.stroke()

        # Fondo de texto
        p.set_graphics_option("fillcolor={ gray 1}")
        p.rect(medX-wCotaWidth/2, mediaExcess+rotuloHeight+50 +
               cropExcess+trimH+cotaSeparation, wCotaWidth, textHeight)
        p.fill()

        p.set_graphics_option(
            "strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")
        p.fit_textline(textCotaW, medX-wCotaWidth/2, mediaExcess +
                       rotuloHeight+50+cropExcess+trimH+cotaSeparation, optlist)

        optlist = optlist+" rotate=90"
        # Izquierda
        p.moveto(mediaExcess+cropExcess+addInfo-cotaSeparation,
                 mediaExcess+rotuloHeight+50+cropExcess)
        p.lineto(mediaExcess+cropExcess+addInfo-cotaSeparation,
                 mediaExcess+rotuloHeight+50+cropExcess+trimH)
        p.stroke()

        # Fondo de texto
        p.set_graphics_option("fillcolor={ gray 1}")
        p.rect(mediaExcess+cropExcess+addInfo-cotaSeparation -
               textHeight, medY-hCotaWidth/2, textHeight, wCotaWidth)
        p.fill()
        p.set_graphics_option(
            "strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")
        p.fit_textline(textCotaH, mediaExcess+cropExcess+addInfo -
                       cotaSeparation, medY-hCotaWidth/2, optlist)

        xGen = mediaExcess+cropExcess
        yGen = mediaExcess+cropExcess + rotuloHeight
        y = yGen
        
        drawLogoColumn( xGen,y)
        drawFirstColumn( xGen+(columnWidth),y)
        drawSecondColumn( xGen+(columnWidth)*2,y)
        nextY=drawThirdColumn( xGen+(columnWidth)*3,y)
        drawFourthColumn( xGen+(columnWidth)*4,nextY)
        drawLastColumn( xGen+(columnWidth)*5,y)
        #Espacio del rotulo
        p.set_graphics_option(
            "strokecolor={ cmyk 0 1 0.88 0} fillcolor={ cmyk 0 0 0 1} linewidth=5")
        p.rect(xGen,mediaExcess+cropExcess, rotuloWidth, rotuloHeight)
        p.stroke()



        p.close_pdi_page(page)
        p.end_page_ext("")
        p.close_pdi_document(unitario)
        p.end_document("")

    except PDFlibException as ex:
        print("PDFlib exception occurred:")
        print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

    except Exception as ex:
        print(ex)

    finally:
        if p:
            p.delete()
