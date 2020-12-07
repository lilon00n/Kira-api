
import sys
import json
from PDFlib.PDFlib import *


def make(searchpath, pdffile, outfile, boxes, colors, percentages, info):
    title = "Nombre de colores"
    p = None
    info = json.loads(info)
    boxes = json.loads(boxes)

    def draw_corner(p, x, y, crop_mark, weight):
        p.save()
        p.translate(x, y)
        p.draw_path(crop_mark, 0, 0, "fill stroke linewidth="+str(weight))
        p.restore()

    def draw_crop_marks(p, x_margin, y_margin, size, weight, dist_height, dist_width, width, height):
        p.set_graphics_option(
            "linewidth="+str(weight)+" fillcolor={spotname All 1} strokecolor={spotname All 1}")

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
        draw_corner(p, x, y, crop_mark, weight)

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
        draw_corner(p, x, y, crop_mark, weight)

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
        draw_corner(p, x, y, crop_mark, weight)

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
        draw_corner(p, x, y, crop_mark, weight)

    def create_registration_mark(p, radius):
        registration_mark = -1
        # Long black lines
        for step in range(0, 2, 1):
            registration_mark = p.add_path_point(registration_mark,
                                                 radius, step * 90,
                                                 "move", "stroke nofill strokecolor={spotname All 1} polar")
            registration_mark = p.add_path_point(registration_mark,
                                                 radius, (step + 2) * 90, "line", "polar")

        # Inner circle
        registration_mark = p.add_path_point(registration_mark,
                                             -radius / 3, 0, "move",
                                             "fill nostroke strokecolor={spotname All 1} fillcolor={spotname All 1}")
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
                                             "stroke nofill strokecolor={spotname All 1}")
        registration_mark = p.add_path_point(registration_mark,
                                             2 * radius / 3, 0, "control", "")
        registration_mark = p.add_path_point(registration_mark, -2
                                             * radius / 3, 0, "circular", "")

        return registration_mark

    def draw_registration_mark(p, x, y, crop_mark):
        p.save()
        p.translate(x, y)
        p.draw_path(crop_mark, 0, 0, "fill stroke")
        p.restore()
    try:
        p = PDFlib()

        searchnalapath = './data'
        p.set_option("searchpath={" + searchnalapath + "}")
        # Open the input PDF */
        nalapdf = p.open_pdi_document('nala-rotulo.pdf', "")
        if nalapdf == -1:
            print("Error: " + p.get_errmsg())
            next

        p.set_option("searchpath={" + searchpath + "}")
        # ### p.set_option("license=w900201-010095-144031-B49YD2-9KN842")

        # This means we must check return values of load_font() etc.
        p.set_option("errorpolicy=return")
        # Open the input PDF */
        indoc = p.open_pdi_document(pdffile, "")
        if indoc == -1:
            print("Error: " + p.get_errmsg())
            next

        endpage = p.pcos_get_number(indoc, "length:pages")
        pageopen = False
        pagewidth = p.pcos_get_number(indoc, "pages[0]/width")
        pageheight = p.pcos_get_number(indoc, "pages[0]/height")
        if p.begin_document(outfile, "") == -1:
            raise "Error: " + p.get_errmsg()

        # Loop over all pages of the input document

        page = p.open_pdi_page(indoc, 1, "pdiusebox=bleed")
        if page == -1:
            print("Error: " + p.get_errmsg())
            next
        nalapage = p.open_pdi_page(nalapdf, 1, "")
        if nalapage == -1:
            print("Error: " + p.get_errmsg())
            next

        bleed0 = float(boxes["bleed"][0])
        bleed1 = float(boxes["bleed"][1])
        trim0 = float(boxes["trim"][0])
        trim1 = float(boxes["trim"][1])
        despX = bleed0-trim0
        despY = bleed1-trim1

        trimW = float(boxes["trimWidth"])*72/25.4
        trimH = float(boxes["trimHeight"])*72/25.4
        nalaheight = p.pcos_get_number(nalapdf, "pages[0]/height")*0.6
        nalawidth = p.pcos_get_number(nalapdf, "pages[0]/width")*0.6
        titles = ["Cliente:", "Vendedor:", "Esp. técnica:", "Archivo:"]
        keys = ["customer", "salesman", "tsCode", "fileName"]
        crop_size = 8
        colorSize = 7
        fsize = 8
        separation = 4
        cotaSeparation = 4*72/25.4  # 12mm del trim,
        bleedExcess = 5*72/25.4  # 5mm
        cropExcess = crop_size*72/25.4  # 8mm
        mediaExcess = 5*72/25.4  # 5mm
        materialMachines = info["materialMachines"]

        # Defino alto del rotulo
        optlist = "fontname=Arial fontsize=" + str(fsize) + " encoding=unicode"
        textHeight = p.info_textline("Un color", "height", optlist)
        percentageWidth = p.info_textline("100.00%  ", "width", optlist)
        tswidth = p.info_textline(" Esp. tecnica:", "width", optlist)
        machinewidth = p.info_textline("Maquina:", "width", optlist)
        heights = []

        colorsHeight = len(colors)*(textHeight+8)
        matMachHeight = len(materialMachines)*2*(textHeight+4)

        heights.append(nalaheight)
        heights.append(colorsHeight)
        heights.append(matMachHeight)

        rotuloHeight = max(heights)+10

        # Defino ancho del rotulo
        # Chequeo donde comenzar a escribir los colores

        maxColor = 0
        for color in colors:
            textwidth = p.info_textline(color, "width", optlist)
            if textwidth > maxColor:
                maxColor = textwidth
        maxInfo = 0
        for index, key in enumerate(keys, start=0):
            textwidth = p.info_textline(info[key], "width", optlist)
            if(textwidth > maxInfo):
                maxInfo = textwidth
        maxMachine = 0
        for mm in materialMachines:
            textwidth = p.info_textline(mm["machine"], "width", optlist)
            if(textwidth > maxMachine):
                maxMachine = textwidth
            textwidth = p.info_textline(mm["material"], "width", optlist)
            if(textwidth > maxMachine):
                maxMachine = textwidth
        infoSize = nalawidth+maxColor+colorSize*2+percentageWidth + \
            tswidth+maxInfo+10+machinewidth+maxMachine+5

        addInfo = 0
        if infoSize > trimW:
            addInfo = (infoSize-trimW)/2

        widths = []
        widths.append(infoSize)
        widths.append(trimW)

        trimbox = "{ "+str(mediaExcess+cropExcess+addInfo)+" "+str(mediaExcess+rotuloHeight+cropExcess)+" "+str(
            mediaExcess+cropExcess+addInfo+trimW) + " "+str(mediaExcess+rotuloHeight+cropExcess+trimH)+" }"
        bleedbox = "{ "+str(mediaExcess+cropExcess+addInfo-bleedExcess)+" "+str(mediaExcess+rotuloHeight+cropExcess-bleedExcess)+" "+str(
            mediaExcess+cropExcess+trimW+addInfo+bleedExcess) + " "+str(mediaExcess+rotuloHeight+cropExcess+trimH+bleedExcess)+" }"
        cropbox = "{ "+str(mediaExcess)+" "+str(mediaExcess)+" "+str(mediaExcess+cropExcess *
                                                                     2+max(widths)) + " "+str(mediaExcess+rotuloHeight+cropExcess*2+trimH)+" }"

        mediaWidth = max(widths)+cropExcess*2+mediaExcess*2
        mediaHeigth = trimH+cropExcess*2+mediaExcess*2+rotuloHeight
        general = p.define_layer("General", "defaultstate=true")
        # Start a new page
        if not pageopen:
            p.begin_page_ext(mediaWidth, mediaHeigth, "trimbox=" +
                             trimbox+" bleedbox="+bleedbox+" cropbox="+cropbox)
            pageopen = True

        p.begin_layer(general)
        # unitario
        p.fit_pdi_page(page, mediaExcess+cropExcess+addInfo+despX,
                       mediaExcess+rotuloHeight+cropExcess+despY, "")

        layerMarks = p.define_layer("Marks", "")
        p.begin_layer(layerMarks)

        # Dibujo marcas de corte
        draw_crop_marks(p, mediaExcess+cropExcess+addInfo,  mediaExcess+rotuloHeight +
                        cropExcess+trimH, crop_size*72/25.4, 0.1, 0, 0, trimW, trimH)

        medX = mediaExcess+cropExcess+addInfo+trimW/2
        medY = mediaExcess+rotuloHeight+cropExcess+trimH/2

        textCotaW = str(round(float(boxes["trimWidth"]), 3))+"mm"
        textCotaH = str(round(float(boxes["trimHeight"]), 3))+"mm"
        # Dibujo cruces de regisro
        p.set_graphics_option(
            "fillcolor={spotname All 0.5} strokecolor={spotname All 0.5} linewidth=0.1")

        wCotaWidth = p.info_textline(textCotaW, "width", optlist)
        hCotaWidth = p.info_textline(textCotaW, "width", optlist+" rotate=90")
        hCotaHeight = p.info_textline(
            textCotaW, "height", optlist+" rotate=90")

        registration_mark = create_registration_mark(p, 5)
        draw_registration_mark(p, medX, mediaExcess+rotuloHeight+cropExcess +
                               trimH+separation+hCotaHeight/2,  registration_mark)  # Top
        draw_registration_mark(p, medX, mediaExcess+rotuloHeight+cropExcess -
                               separation-hCotaHeight/2,  registration_mark)  # Bottom
        draw_registration_mark(p, mediaExcess+cropExcess+addInfo -
                               separation-hCotaHeight/2, medY,  registration_mark)  # Left
        draw_registration_mark(p, mediaExcess+cropExcess+addInfo+trimW +
                               separation+hCotaHeight/2, medY,  registration_mark)  # Right

        p.set_graphics_option("strokecolor={ cmyk 0 0 0 1}")

        # Dibujo cotas
        # Superior
        p.moveto(mediaExcess+cropExcess+addInfo, mediaExcess +
                 rotuloHeight+cropExcess+trimH+cotaSeparation)
        p.lineto(mediaExcess+cropExcess+addInfo+trimW, mediaExcess +
                 rotuloHeight+cropExcess+trimH+cotaSeparation)
        p.stroke()

        # Fondo de texto
        p.set_graphics_option("fillcolor={ gray 1}")
        p.rect(medX-wCotaWidth/2, mediaExcess+rotuloHeight +
               cropExcess+trimH+cotaSeparation, wCotaWidth, textHeight)
        p.fill()

        p.set_graphics_option(
            "strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")
        p.fit_textline(textCotaW, medX-wCotaWidth/2, mediaExcess +
                       rotuloHeight+cropExcess+trimH+cotaSeparation, optlist)

        optlist = optlist+" rotate=90"
        # Izquierda
        p.moveto(mediaExcess+cropExcess+addInfo-cotaSeparation,
                 mediaExcess+rotuloHeight+cropExcess)
        p.lineto(mediaExcess+cropExcess+addInfo-cotaSeparation,
                 mediaExcess+rotuloHeight+cropExcess+trimH)
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

        xGen = mediaExcess+cropExcess + nalawidth + maxColor + 10
        yGen = mediaExcess+rotuloHeight
        y = yGen

        # Dibujo colores
        for index, color in enumerate(colors, start=0):
            if "PANTONE" in color:
                optlist = "fontname=Arial fontsize=" + \
                    str(fsize) + \
                    " encoding=unicode fillcolor={ spotname {" + color + "} 1}"
            else:
                optlist = "fontname=Arial fontsize=" + \
                    str(fsize) + \
                    " encoding=unicode fillcolor={ " + color + " }"

            textline = color
            textwidth = p.info_textline(textline, "width", optlist)

            p.fit_textline(textline, xGen-textwidth, y, optlist)

            p.fit_textline(percentages[index]+"%", xGen+20, y, optlist)

            if "PANTONE" in color:
                p.set_graphics_option(
                    "fillcolor={ spotname { " + color + "} 1}")
                p.rect(xGen+2, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option(
                    "fillcolor={ spotname { " + color + "} 0.7}")
                p.rect(xGen+2, y, colorSize, 4)
                p.fill()
                p.set_graphics_option(
                    "fillcolor={ spotname { " + color + "} 0.5}")
                p.rect(xGen+2+colorSize, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option(
                    "fillcolor={ spotname { " + color + "} 0.2}")
                p.rect(xGen+2+colorSize, y, colorSize, 4)
                p.fill()

                p.set_graphics_option(
                    "strokecolor={ spotname { " + color + "} 1}")
            if color == "Cyan":
                p.set_graphics_option("fillcolor={ cmyk 1 0 0 0 }")
                p.rect(xGen+2, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0.7 0 0 0 }")
                p.rect(xGen+2, y, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0.5 0 0 0 }")
                p.rect(xGen+2+colorSize, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0.2 0 0 0 }")
                p.rect(xGen+2+colorSize, y, colorSize, 4)
                p.fill()

                p.set_graphics_option("strokecolor={ cmyk 1 0 0 0 }")
            if color == "Magenta":
                p.set_graphics_option("fillcolor={ cmyk 0 1 0 0 }")
                p.rect(xGen+2, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0.7 0 0 }")
                p.rect(xGen+2, y, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0.5 0 0 }")
                p.rect(xGen+2+colorSize, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0.2 0 0 }")
                p.rect(xGen+2+colorSize, y, colorSize, 4)
                p.fill()

                p.set_graphics_option("strokecolor={ cmyk 0 1 0 0 }")
            if color == "Yellow":
                p.set_graphics_option("fillcolor={ cmyk 0 0 1 0 }")
                p.rect(xGen+2, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0.7 0 }")
                p.rect(xGen+2, y, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0.5 0 }")
                p.rect(xGen+2+colorSize, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0.2 0 }")
                p.rect(xGen+2+colorSize, y, colorSize, 4)
                p.fill()

                p.set_graphics_option("strokecolor={ cmyk 0 0 1 0 }")
            if color == "Black":
                p.set_graphics_option("fillcolor={ cmyk 0 0 0 1}")
                p.rect(xGen+2, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0 0.7}")
                p.rect(xGen+2, y, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0 0.5}")
                p.rect(xGen+2+colorSize, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ cmyk 0 0 0 0.2}")
                p.rect(xGen+2+colorSize, y, colorSize, 4)
                p.fill()

                p.set_graphics_option("strokecolor={ cmyk 0 0 0 1}")
            if color == "Red":
                p.set_graphics_option("fillcolor={ rgb 1 0 0 }")
                p.rect(xGen+2, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0.7 0 0 }")
                p.rect(xGen+2, y, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0.5 0 0 }")
                p.rect(xGen+2+colorSize, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0.2 0 0 }")
                p.rect(xGen+2+colorSize, y, colorSize, 4)
                p.fill()

                p.set_graphics_option("strokecolor={ rgb 1 0 0 }")
            if color == "Green":
                p.set_graphics_option("fillcolor={ rgb 0 1 0 }")
                p.rect(xGen+2, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0.7 0 }")
                p.rect(xGen+2, y, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0.5 0 }")
                p.rect(xGen+2+colorSize, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0.2 0 }")
                p.rect(xGen+2+colorSize, y, colorSize, 4)
                p.fill()

                p.set_graphics_option("strokecolor={ rgb 0 1 0 }")
            if color == "Blue":
                p.set_graphics_option("fillcolor={ rgb 0 0 1 }")
                p.rect(xGen+2, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0 0.7 }")
                p.rect(xGen+2, y, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0 0.5 }")
                p.rect(xGen+2+colorSize, y+4, colorSize, 4)
                p.fill()
                p.set_graphics_option("fillcolor={ rgb 0 0 0.2 }")
                p.rect(xGen+2+colorSize, y, colorSize, 4)
                p.fill()

                p.set_graphics_option("strokecolor={ rgb 0 0 1 }")

            # Dibujo la linea separdora
            p.moveto(2*crop_size*72/25.4 + nalawidth, y-2)
            p.lineto(xGen + colorSize*2+percentageWidth, y-2)
            p.stroke()

            y = y-textHeight-8

        # Escribo infos
        optlist = "fontname=Arial fontsize=" + \
            str(fsize)+" encoding=unicode fillcolor={ Black }"

        xGen = xGen+colorSize*2+percentageWidth+5+tswidth
        y = yGen
        maxTextWidth = 0
        p.set_graphics_option("strokecolor={ cmyk 0 0 0 1}")

        for index, key in enumerate(keys, start=0):
            textline = titles[index]
            textwidth = p.info_textline(textline, "width", optlist)
            p.fit_textline(textline, xGen-textwidth, y, optlist)

            p.moveto(xGen-textwidth, y-2)
            p.lineto(xGen, y-2)
            p.stroke()
            textline = info[key]
            textwidth = p.info_textline(textline, "width", optlist)
            p.fit_textline(textline, xGen+2, y, optlist)

            if(textwidth > maxTextWidth):
                maxTextWidth = textwidth

            y = y-textHeight-4

        xGen = xGen+maxTextWidth+tswidth
        y = yGen
        materialwidth = p.info_textline("Material:", "width", optlist)
        for mm in materialMachines:
            p.fit_textline("Maquina:", xGen-machinewidth, y, optlist)
            p.moveto(xGen-machinewidth, y-2)
            p.lineto(xGen, y-2)
            p.stroke()
            p.fit_textline(mm["machine"], xGen+2, y, optlist)
            y = y-textHeight-4

            p.fit_textline("Material:", xGen-materialwidth, y, optlist)
            p.moveto(xGen-materialwidth, y-2)
            p.lineto(xGen, y-2)
            p.stroke()
            p.fit_textline(mm["material"], xGen+2, y, optlist)
            y = y-textHeight-4

            # imagen nalav
        p.fit_pdi_page(nalapage, mediaExcess+cropExcess,
                       mediaExcess+rotuloHeight-nalaheight, "scale={0.6 0.6}")
        p.close_pdi_page(nalapage)
        p.close_pdi_document(nalapdf)

        p.end_layer()
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
