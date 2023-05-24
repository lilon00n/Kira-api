
import sys
import json
from PDFlib.PDFlib import *
from make_devicen import make_devicen
from clients import findClient

POINT_TO_MM_FACTOR = 72 / 25.4
TITLES = ["Cliente:", "Vendedor:", "Esp. técnica:", "Archivo:", "Tipo de producto:","Tipo de código:", "No. Barras","Diseñador"]
KEYS = ["customer", "salesman", "tsCode", "fileName","productType","barcodeType","barcodeNumber","designer"]
CROP_SIZE = 8
SQUARE_COLOR_SIZE = 7
FONT_SIZE = 8
CROP_MARK_SEPARATION = 4
COTA_SEPARATION = 5*POINT_TO_MM_FACTOR
CRUZ_SEPARATION = 3*POINT_TO_MM_FACTOR
BLEED_EXCESS = 5*POINT_TO_MM_FACTOR
CROP_EXCESS = CROP_SIZE*POINT_TO_MM_FACTOR 
MEDIA_EXCESS = 5*POINT_TO_MM_FACTOR
SEARCH_DATA_PATH = './data'
def draw_corner(p, x, y, crop_mark, weight):
    p.save()
    p.translate(x, y)
    p.draw_path(crop_mark, 0, 0, "fill stroke linewidth="+str(weight))
    p.restore()

def draw_crop_marks(p, x_margin, y_margin, size, weight, dist_height, dist_width, width, height):
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
        crop_mark, 0, int(-dist_height), "move", "stroke nofill")
    crop_mark = p.add_path_point(
        crop_mark, 0, int(-size - dist_height), "line", "")
    crop_mark = p.add_path_point(crop_mark, int(
        dist_width), 0, "move", "stroke nofill")
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

def draw_registration_mark(p, x, y, crop_mark):
    p.save()
    p.translate(x, y)
    p.draw_path(crop_mark, 0, 0, "fill stroke")
    p.restore()

def draw_registration_marks(p, label_height, boxes, add_info):
    registration_mark = create_registration_mark(p, 5)
    trim_width, trim_height = get_trim_size(boxes)
    text_height= get_text_heigth(p)
    center_x = MEDIA_EXCESS + CROP_EXCESS + add_info + trim_width / 2
    center_y = MEDIA_EXCESS + label_height + CROP_EXCESS + trim_height / 2

    top_y = MEDIA_EXCESS + label_height + CROP_EXCESS + trim_height + CROP_MARK_SEPARATION + text_height / 2 + CRUZ_SEPARATION
    bottom_y = MEDIA_EXCESS + label_height + CROP_EXCESS - CROP_MARK_SEPARATION - text_height / 2 - CRUZ_SEPARATION
    left_x = MEDIA_EXCESS + CROP_EXCESS + add_info - CROP_MARK_SEPARATION - text_height / 2 - CRUZ_SEPARATION
    right_x = MEDIA_EXCESS + CROP_EXCESS + add_info + trim_width + CROP_MARK_SEPARATION + text_height / 2 + CRUZ_SEPARATION

    # Draw the top registration mark
    draw_registration_mark(p, center_x, top_y,  registration_mark)

    # Draw the bottom registration mark
    draw_registration_mark(p, center_x, bottom_y,  registration_mark)
    
    # Draw the left registration mark
    draw_registration_mark(p, left_x, center_y,  registration_mark)
    
    # Draw the right registration mark
    draw_registration_mark(p, right_x, center_y,  registration_mark)
    
    return

def draw_cotas(p, label_height, boxes, add_info ):
    # Get trim size
    trim_width, trim_height = get_trim_size(boxes)
    optlist = get_text_optlist()

    # Calculate center points
    center_x = MEDIA_EXCESS + CROP_EXCESS + add_info + trim_width / 2
    center_y = MEDIA_EXCESS + CROP_EXCESS + label_height  + trim_height / 2

    # Get box dimensions as text
    cota_x_text = str(round(float(boxes["trimWidth"]), 3)) + "mm"
    cota_y_text = str(round(float(boxes["trimHeight"]), 3)) + "mm"

    # Get text width for different labels
    cota_x_width = p.info_textline(cota_x_text, "width", optlist)
    cota_y_width = p.info_textline(cota_y_text, "width", optlist + " rotate=90")

    # Draw labels
    draw_label_x(p, center_x, trim_width, trim_height, cota_x_width, cota_x_text, add_info, label_height, optlist)
    optlist += " rotate=90"
    draw_label_y(p, center_y, trim_height, cota_y_width, cota_y_text, add_info, label_height, optlist)

def draw_label_x(p, center_x, trim_width, trim_height, cota_x_width, cota_x_text, add_info, label_height, optlist):
    text_height= get_text_heigth(p)
    # Upper
    start_x = MEDIA_EXCESS + CROP_EXCESS + add_info
    start_y = MEDIA_EXCESS + label_height + CROP_EXCESS + trim_height + COTA_SEPARATION
    p.moveto(start_x, start_y)
    p.lineto(start_x + trim_width, start_y)
    p.stroke()

    # Text background
    p.set_graphics_option("fillcolor={ gray 1}")
    p.rect(center_x - cota_x_width / 2, start_y, cota_x_width, text_height)
    p.fill()

    p.set_graphics_option("strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")
    p.fit_textline(cota_x_text, center_x - cota_x_width / 2, start_y, optlist)

def draw_label_y(p, center_y, trim_height, cota_y_width, cota_y_text, add_info, label_height, optlist):
    text_height= get_text_heigth(p)
    # Left
    start_x = MEDIA_EXCESS + CROP_EXCESS + add_info - COTA_SEPARATION
    start_y = MEDIA_EXCESS + label_height + CROP_EXCESS

    p.moveto(start_x, start_y)
    p.lineto(start_x, start_y + trim_height)
    p.stroke()

    # Text background
    p.set_graphics_option("fillcolor={ gray 1}")
    p.rect(start_x - text_height, center_y - cota_y_width / 2, text_height, cota_y_width)
    p.fill()

    p.set_graphics_option("strokecolor={ cmyk 0 0 0 1} fillcolor={ cmyk 0 0 0 1}")
    p.fit_textline(cota_y_text, start_x - text_height, center_y - cota_y_width / 2, optlist)
   
def load_client_logo(p, client):
    logo_client = p.load_image(client.ext, client.logo, "page=1")
    if logo_client == -1:
        print_error(p)
    return logo_client

def load_pdf_document(p, path):
    pdfdoc = p.open_pdi_document(path, "")
    if pdfdoc == -1:
        print_error(p)
    return pdfdoc

def get_pdf_page(p, pdf, options):
    page= p.open_pdi_page(pdf, 1, options)
    if page == -1:
        print_error(p)
    return page

def print_error(p):
    print("Error: " + p.get_errmsg())

def load_body_information(client, outfile, boxes, info):
    client = findClient(client)
    title = get_output_file_title(outfile)
    info = json.loads(info)
    boxes = json.loads(boxes)
    return client, title, boxes, info

def get_output_file_title(outfile):
    paths = outfile.split("\\") if "\\" in outfile else outfile.split("/")
    return paths[-1]

def get_bleed_trim_gap(boxes):
    bleed0 = float(boxes["bleed"][0])
    bleed1 = float(boxes["bleed"][1])
    trim0 = float(boxes["trim"][0])
    trim1 = float(boxes["trim"][1])
    despX = bleed0-trim0
    despY = bleed1-trim1
    return despX, despY

def get_trim_size(boxes):
    trimW = float(boxes["trimWidth"])*POINT_TO_MM_FACTOR
    trimH = float(boxes["trimHeight"])*POINT_TO_MM_FACTOR
    return trimW, trimH

def calculate_optlist(p, devicen, colorsJson, index):
    ceros, cero7, cero5, cero2 = "", "", "", ""
    for x in range(len(colorsJson)):
        if (x == index):
            ceros, cero7, cero5, cero2 = ceros + "1 ", cero7 + "0.7 ", cero5 + "0.5 ", cero2 + "0.2 "
        else:
            ceros, cero7, cero5, cero2 = ceros + "0 ", cero7 + "0 ", cero5 + "0 ", cero2 + "0 "

    optlist = f"fontname=Arial fontsize={FONT_SIZE} encoding=unicode fillcolor={{devicen {devicen} {ceros}}}"
    return ceros, cero7, cero5, cero2, optlist

def draw_separator_line(p, maxLogo, xGen, y):
    max_color_percentage = get_max_color_percentage(p)
    # Dibujo la linea separdora
    p.moveto(2*CROP_SIZE*POINT_TO_MM_FACTOR + maxLogo, y-2)
    p.lineto(xGen + SQUARE_COLOR_SIZE*2+max_color_percentage, y-2)
    p.stroke()

def draw_color_lines(p, xGen, y, color, devicen, ceros, cero7, cero5, cero2, optlist):
    colorname = color["name"]
    textwidth = p.info_textline(colorname, "width", optlist)
    p.fit_textline(colorname, xGen-textwidth, y, optlist)
    p.fit_textline(color["inkCov"]+"%", xGen+20, y, optlist)
    p.set_graphics_option(
        f"fillcolor={{ devicen {devicen} {ceros}}}")
    p.rect(xGen+2, y+4, SQUARE_COLOR_SIZE, 4)
    p.fill()
    p.set_graphics_option(
        f"fillcolor={{ devicen {devicen} {cero7}}}")
    p.rect(xGen+2, y, SQUARE_COLOR_SIZE, 4)
    p.fill()
    p.set_graphics_option(
        f"fillcolor={{ devicen {devicen} {cero5}}}")
    p.rect(xGen+2+SQUARE_COLOR_SIZE, y+4, SQUARE_COLOR_SIZE, 4)
    p.fill()
    p.set_graphics_option(
        f"fillcolor={{ devicen {devicen} {cero2}}}")
    p.rect(xGen+2+SQUARE_COLOR_SIZE, y, SQUARE_COLOR_SIZE, 4)
    p.fill()
    p.set_graphics_option(
        f"strokecolor={{ devicen {devicen} {ceros}}}")
    
def get_text_optlist():
    optlist = "fontname=Arial fontsize=" + str(FONT_SIZE) + " encoding=unicode"
    return optlist

def get_text_heigth(p):
    optlist = get_text_optlist()
    text_height = p.info_textline("Un color", "height", optlist)
    return text_height

def get_label_height(p, colorsJson, info, nala_height, logo_client_height):
    text_height= get_text_heigth(p)
    material_machines = info["materialMachines"]
    heights = []
    colors_height = len(colorsJson)*(text_height+8)
    mat_mach_height = len(material_machines)*2*(text_height+4)
    infos_height = len(TITLES)*(text_height+4)
    

    heights.append(nala_height+10+logo_client_height)
    heights.append(infos_height)
    heights.append(colors_height)
    heights.append(mat_mach_height)

    label_height = max(heights)+10
    return label_height

def get_max_color_width(p, colorsJson):
    optlist = get_text_optlist()
    max_color_width = max([p.info_textline(color["name"], "width", optlist) for color in colorsJson])
    return max_color_width

def get_max_info_width(p, info):
    optlist = get_text_optlist()
    max_info = max(p.info_textline(info[key], "width", optlist) for key in KEYS)
    return max_info

def get_max_machine_width(p, material_machines):
    optlist = get_text_optlist()
    max_machine = max(
        max(p.info_textline(mm["machine"], "width", optlist), p.info_textline(mm["material"], "width", optlist))
        for mm in material_machines
    )
    return max_machine

def get_logo_width(p, logo_client):
    logo_width = p.info_image(logo_client, "width", "scale=0.05")
    return logo_width

def get_max_color_percentage(p):
    optlist = get_text_optlist()
    max_color_percentage = p.info_textline("100.00%  ", "width", optlist)
    return max_color_percentage

def get_max_info_key(p):
    optlist = get_text_optlist()
    max_info_key = p.info_textline(" Tipo de producto:", "width", optlist)
    return max_info_key

def get_machine_key(p):
    optlist = get_text_optlist()
    machine_key = p.info_textline("Maquina:", "width", optlist)
    return machine_key

def get_salida_width(p):
    optlist = get_text_optlist()
    salida_width = p.info_textline("Salida:", "width", optlist)
    return salida_width

def get_keys_width(p, colorsJson, info, logo_client):
    material_machines = info["materialMachines"]
    max_color_percentage = get_max_color_percentage(p)
    max_info_key = get_max_info_key(p)
    max_machine_key = get_machine_key(p)
    salida_width = get_salida_width(p)
    max_color_name = get_max_color_width(p, colorsJson)
    max_info = get_max_info_width(p, info)
    max_machine = get_max_machine_width(p, material_machines)
    max_logo = get_logo_width(p, logo_client)
    return max_color_percentage, max_info_key, max_machine_key, salida_width, max_color_name, max_info, max_machine, max_logo

def get_label_width(p, colorsJson, info, logo_client):
    max_color_percentage, max_info_key, max_machine_key, salida_width, max_color_name, max_info, max_machine, max_logo = get_keys_width(p, colorsJson, info, logo_client)

    logo_color_gap = 10
    total_color = max_color_name + logo_color_gap + SQUARE_COLOR_SIZE*2 + max_color_percentage

    color_info_gap = 15
    total_info = max_info_key + color_info_gap + max_info

    info_machine_gap = 10
    total_machine = max_machine_key + info_machine_gap + max_machine

    salida_img_width = 25
    total_salida = salida_width + salida_img_width

    label_width = max_logo + total_color + total_info + total_machine + total_salida
    return label_width

def get_total_width(label_width, trimW):
    widths = []
    widths.append(label_width)
    widths.append(trimW)
    return max(widths)

def get_add_info(label_width, trimW):
    add_info = 0
    if label_width > trimW:
        add_info = (label_width-trimW)/2
    return add_info

def generate_box_string(x1, y1, x2, y2):
    return f"{{ {x1} {y1} {x2} {y2} }}"

def get_boxes_size(label_height, trimW, trimH, total_width, add_info):
    baseX = MEDIA_EXCESS + CROP_EXCESS + add_info
    baseY = MEDIA_EXCESS + CROP_EXCESS + label_height 
    trimbox = generate_box_string(baseX, baseY, baseX+trimW, baseY+trimH)
    
    baseX_bleed = baseX - BLEED_EXCESS
    baseY_bleed = baseY - BLEED_EXCESS
    bleedbox = generate_box_string(baseX_bleed, baseY_bleed, baseX_bleed+trimW+BLEED_EXCESS, baseY_bleed+trimH+BLEED_EXCESS)
    
    baseX_crop = MEDIA_EXCESS
    baseY_crop = MEDIA_EXCESS
    cropbox = generate_box_string(baseX_crop, baseY_crop, baseX_crop+CROP_EXCESS*2+total_width, baseY_crop+label_height+CROP_EXCESS*2+trimH)

    return trimbox, bleedbox, cropbox


def draw_colors_section(p, x, y, colorsJson, devicen, max_logo):
    max_color_name = get_max_color_width(p, colorsJson)
    x += max_color_name
    text_height= get_text_heigth(p)
    # Dibujo colores
    for index, color in enumerate(colorsJson, start=0):
        ceros, cero7, cero5, cero2, optlist = calculate_optlist(p, devicen, colorsJson, index)
        draw_color_lines(p, x, y, color, devicen, ceros, cero7, cero5, cero2, optlist)
        draw_separator_line(p, max_logo, x, y)

        y = y-text_height-8
    return x

def draw_info_section(p, x, y, info):
    text_height= get_text_heigth(p)
    max_info_key = get_max_info_key(p)
    max_color_percentage = get_max_color_percentage(p)
    max_info = get_max_info_width(p, info)
    
    # Escribo infos
    optlist = "fontname=Arial fontsize=" + \
        str(FONT_SIZE)+" encoding=unicode fillcolor={ Black }"
    
    x = x+SQUARE_COLOR_SIZE*2+max_color_percentage+5+max_info_key
    p.set_graphics_option("strokecolor={ cmyk 0 0 0 1}")

    for index, key in enumerate(KEYS, start=0):
        textline = TITLES[index]
        textwidth = p.info_textline(textline, "width", optlist)
        p.fit_textline(textline, x-textwidth, y, optlist)

        p.moveto(x-textwidth, y-2)
        p.lineto(x, y-2)
        p.stroke()
        textline = info[key]
        textwidth = p.info_textline(textline, "width", optlist)
        p.fit_textline(textline, x+2, y, optlist)
        y = y-text_height-4

    x += max_info
    x += max_info_key
    return x

def draw_machine_section(p, x, y, info):
    material_machines = info["materialMachines"]
    optlist = get_text_optlist()
    text_height= get_text_heigth(p)
    max_machine = get_max_machine_width(p, material_machines)
    max_machine_key = get_machine_key(p)

    # Escribo materiales
    materialwidth = p.info_textline("Material:", "width", optlist)
    
    for mm in material_machines:
        p.fit_textline("Maquina:", x-max_machine_key, y, optlist)
        p.moveto(x-max_machine_key, y-2)
        p.lineto(x, y-2)
        p.stroke()
        p.fit_textline(mm["machine"], x+2, y, optlist)
        y = y-text_height-4

        p.fit_textline("Material:", x-materialwidth, y, optlist)
        p.moveto(x-materialwidth, y-2)
        p.lineto(x, y-2)
        p.stroke()
        p.fit_textline(mm["material"], x+2, y, optlist)
        y = y-text_height-4
    x += max_machine
    return x

def load_salida_img(p, salida):
    searchpath = './data/embobinado'
    p.set_option("searchpath={{" + searchpath + "}}")
    img_salida = p.load_image('png',salida, "page=1")
    img_salida_height = p.info_image(img_salida, "height", "scale=0.25")
    
    if img_salida == -1:
        print("Error: " + p.get_errmsg())
        next
    return img_salida, img_salida_height

def draw_salida_section(p, x, y, salida):
    salida += '.png'
    salida_width = get_salida_width(p)
    optlist = get_text_optlist()
    text_height= get_text_heigth(p)
    x = x+salida_width
    img_salida, img_salida_height = load_salida_img(p, salida)

    p.fit_textline("Salida:", x, y, optlist)
    p.fit_image(img_salida, x, y-text_height-img_salida_height-4, "scale=0.25")

def get_nala_pdf(p):
    # Open the input PDF, Nala PDF for the label */
    p.set_option("searchpath={" + SEARCH_DATA_PATH + "}")
    nalapdf = load_pdf_document(p, 'nala-rotulo.pdf')
    nalapage = get_pdf_page(p, nalapdf, "")
    nala_height = p.pcos_get_number(nalapdf, "pages[0]/height")*0.6
    return nalapdf, nalapage, nala_height

def get_logo_client(p, client):
    p.set_option("searchpath={" + SEARCH_DATA_PATH + "}")
    logo_client = load_client_logo(p, client)
    logo_client_height = p.info_image(logo_client, "height", "scale=0.05")
    return logo_client, logo_client_height

def get_pdf_unitario(p, pdffile, searchpath) :
    p.set_option("searchpath={" + searchpath + "}")
    unitario = load_pdf_document(p, pdffile)
    page = get_pdf_page(p, unitario, "pdiusebox=bleed")
    unitario_height = p.pcos_get_number(unitario, "pages[0]/height")
    unitario_width = p.pcos_get_number(unitario, "pages[0]/width")
    return unitario, page, unitario_height,unitario_width

def add_separation_pages(p, separations_folder, path_images, names, width, height):
    for index, image in enumerate(path_images, start=0):
        tif = p.load_image("tiff", separations_folder+image, "page=1")
        if tif == -1:
            print("Error: " + p.get_errmsg())
            next

        # Start a new page
        p.begin_page_ext(float(width), float(height)+10, "")
        p.fit_image(tif, 0.0, 10, "adjustpage")
        p.close_image(tif)
        optlist = "fontname=Helvetica fontsize=10 encoding=unicode  fillcolor={ Black }"

        textline = names[index]
        p.fit_textline(textline, 0, 0, optlist)
        p.end_page_ext("")
        print(image)

def make(searchpath, pdffile, outfile, client, boxes, colorsJson, info, separations_folder, path_images, names):
    client, title, boxes, info = load_body_information(client, outfile, boxes, info)

    try:
        p = PDFlib()
        # Set license key
        p.set_option("license=w900202-010598-802290-LJJBF2-BEC8G2")
        # This means we must check return values of load_font() etc.
        p.set_option("errorpolicy=return")

        pageopen = False
        if p.begin_document(outfile, "") == -1:
            print_error(p)

        # Get Nala PDF for label
        nalapdf, nalapage, nala_height = get_nala_pdf(p)
        # Open the input PDF unitario */
        unitario, page, unitario_height, unitario_width = get_pdf_unitario(p, pdffile, searchpath)
        # Open client logo
        logo_client, logo_client_height = get_logo_client(p, client)

        despX, despY = get_bleed_trim_gap(boxes)
        trimW, trimH = get_trim_size(boxes)
    
        devicen = make_devicen(p, colorsJson)
        
        # Define height for the label
        label_height = get_label_height(p, colorsJson, info, nala_height, logo_client)    
        # Define width for the label
        label_width = get_label_width(p, colorsJson, info, logo_client)

        # Chequeo donde comenzar a escribir los colores
        total_width = get_total_width(label_width, trimW)
        add_info = get_add_info(label_width, trimW)

        trimbox, bleedbox, cropbox = get_boxes_size(label_height, trimW, trimH, total_width, add_info)

        mediaWidth = total_width+CROP_EXCESS*2+MEDIA_EXCESS*2
        mediaHeight = trimH+label_height+CROP_EXCESS*2+MEDIA_EXCESS*2

        max_logo = get_logo_width(p, logo_client)

        # Start a new page
        if not pageopen:
            p.begin_page_ext(mediaWidth, mediaHeight, "trimbox=" +
                             trimbox+" bleedbox="+bleedbox+" cropbox="+cropbox)
            pageopen = True

        # Fit PDF unitario
        p.fit_pdi_page(page, MEDIA_EXCESS+CROP_EXCESS+add_info+despX,
                       MEDIA_EXCESS+label_height+CROP_EXCESS+despY, "")
        
        # Fit PDF nala
        p.fit_pdi_page(nalapage, MEDIA_EXCESS+CROP_EXCESS,
                       MEDIA_EXCESS+label_height-nala_height, "scale={0.6 0.6}")
        p.close_pdi_page(nalapage)
        p.close_pdi_document(nalapdf)

        # Fit IMG logo client
        p.fit_image(logo_client, MEDIA_EXCESS+CROP_EXCESS,
                    MEDIA_EXCESS+label_height-nala_height-10-logo_client_height, "scale=0.05")
        p.close_image(logo_client)

        # Dibujo cruces de regisro
        ones = ""
        for x in range(len(colorsJson)):
            ones = ones + "1 "

        p.set_graphics_option("fillcolor={devicen " + str(devicen)+" " + ones +
                              "} strokecolor={devicen " + str(devicen)+" " + ones + "} linewidth=0.01")

        # Dibujo marcas de corte
        draw_crop_marks(p, MEDIA_EXCESS+CROP_EXCESS+add_info,  MEDIA_EXCESS+label_height +
                        CROP_EXCESS+trimH, CROP_SIZE*POINT_TO_MM_FACTOR, 0.01, 0, 0, trimW, trimH)

        # Dibujo marcas de registro
        draw_registration_marks(p, label_height, boxes, add_info)

        # Dibujo cotas
        draw_cotas(p, label_height, boxes, add_info)

        xGen = MEDIA_EXCESS + CROP_EXCESS + max_logo + 10
        yGen = MEDIA_EXCESS + label_height - 10
        
        # Dibujo seccion de colores
        xGen = draw_colors_section(p, xGen, yGen, colorsJson, devicen, max_logo)

        # Dibujo seccion de info
        xGen = draw_info_section(p, xGen, yGen, info)

        # Dibujo seccion de maquinas
        xGen = draw_machine_section(p, xGen, yGen, info)
        

        salida = info["salida"]
        #Escribo salida 
        if salida != '':
            draw_salida_section(p, x, yGen, salida)
            
            
        p.close_pdi_page(page)
        p.end_page_ext("")

        #agrego las demas paginas con las separaciones
        add_separation_pages(p, separations_folder, path_images, names, unitario_width, unitario_height)
        
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
