#!/usr/bin/python
#
# PDFlib+PDI client: invoice generation demo #

from PDFlib.PDFlib import *
import time

x_table = 55
tablewidth = 475

y_address = 682
x_salesrep = 455
y_invoice = 542
imagesize = 90

fontsize = 11
fontsizesmall = 9

fontname= "NotoSerif-Regular"


date = time.strftime("%x", time.gmtime(time.time()))

# -----------------------------------
# Place company stationery as background
# -----------------------------------

def create_stationery(p):
    
    sender = \
        "Kraxi Systems, Inc. &#x2022; 17, Aviation Road &#x2022; Paperfield"
    stationeryfontname= "NotoSerif-Regular"

    stationeryfilename = "kraxi_logo.pdf"

    y_company_logo = 748

    senderfull = \
        "17, Aviation Road\n" \
        "Paperfield<nextline leading=50%><nextparagraph leading=120%>" \
        "Phone 7079-4301\n" \
        "Fax 7079-4302<nextline leading=50%><nextparagraph leading=120%>" \
        "info@kraxi.com\n" \
        "www.kraxi.com\n"

    stationery = p.open_pdi_document(stationeryfilename, "")
    page = p.open_pdi_page(stationery, 1, "")

    p.fit_pdi_page(page, 0, y_company_logo,
            "boxsize={595 85} position={65 center}")
    p.close_pdi_page(page)
    p.close_pdi_document(stationery)

    optlist =  basefontoptions + " fontsize=" + repr(fontsizesmall) + \
        " fontname=" + stationeryfontname + " charref=true"
    p.fit_textline(sender, x_table, y_address + fontsize,
            optlist)

    # -----------------------------------
    # Print full company contact details
    # -----------------------------------
    
    optlist = basefontoptions + " fontname=" + stationeryfontname + \
    " leading=125% fillcolor={cmyk 0.64 0.55 0.52 0.27}"
    tf = p.create_textflow(senderfull, optlist)
    p.fit_textflow(tf, x_salesrep, y_address, \
            x_salesrep+imagesize, y_address + 150, "verticalalign=bottom")
    p.delete_textflow(tf)

# -----------------------------------
# Place address and header text
# -----------------------------------

def create_header(p):
    salesrepfilename = "sales_rep4.jpg"
    salesrepname = "Lucy Irwin"
    salesrepcaption = "Local sales rep:"
    invoiceheader = "INVOICE 2012-03"

    address = \
        "John Q. Doe\n" \
        "255 Customer Lane\n" \
        "Suite B\n" \
        "12345 User Town\n" \
        "Everland"

    # -----------------------------------
    # Print address
    # -----------------------------------
    
    optlist = basefontoptions + " leading=120%"

    tf = p.create_textflow(address, optlist)
    p.fit_textflow(tf,
            x_table, y_address, x_table+tablewidth/2, y_address-100, "")
    p.delete_textflow(tf)

    # -----------------------------------
    # Place name and image of local sales rep
    # -----------------------------------

    optlist = basefontoptions + " fontsize=" + repr(fontsizesmall)
    p.fit_textline(salesrepcaption, x_salesrep, y_address-fontsizesmall,
            optlist)
    p.fit_textline(salesrepname, x_salesrep, y_address-2*fontsizesmall,
            optlist)

    salesrepimage = p.load_image("auto", salesrepfilename, "")

    optlist = "boxsize={" + repr(imagesize) + " " +  repr(imagesize) + "} fitmethod=meet"
    p.fit_image(salesrepimage,
            x_salesrep, y_address-3*fontsizesmall-imagesize, optlist)
    p.close_image(salesrepimage)

    # -----------------------------------
    # Print the header and date
    # -----------------------------------

    # Add a bookmark with the header text 
    p.create_bookmark(invoiceheader, "")

    optlist =  basefontoptions
    p.fit_textline(invoiceheader, x_table, y_invoice, optlist)

    date = time.strftime("%B %-d, %Y")

    optlist =  "position {100 0} " + basefontoptions
    p.fit_textline(date, x_table+tablewidth, y_invoice, optlist)



# This is where font/image/PDF input files live. Adjust as necessary. 
searchpath = "../data"

closingtext = \
"Terms of payment: <fillcolor={rgb 1 0 0}>30 days net. " \
"<fillcolor={gray 0}>90 days warranty starting at the day of sale. " \
"This warranty covers defects in workmanship only. " \
"Kraxi Systems, Inc. will, at its option, repair or replace the " \
"product under the warranty. This warranty is not transferable. " \
"No returns or exchanges will be accepted for wet products."

dataset = [
  [ "Super Kite",          20,  2],
  [ "Turbo Flyer",         40,  5],
  [ "Giga Trash",          180, 1],
  [ "Bare Bone Kit",       50,  3],
  [ "Nitty Gritty",        20,  10],
  [ "Pretty Dark Flyer",   75,  1],
  [ "Free Gift",           0,   1]
]

headers = [ "ITEM", "DESCRIPTION", "QUANTITY", "PRICE", "AMOUNT"]

alignments = [ "right", "left", "right", "right", "right"]

p = None

try: 
    p = PDFlib()

    pagecount = 0
    top = 0

    p.set_option("SearchPath={{" + searchpath + "}}")

    # This mean we don't have to check error return values, but will
    # get an exception in case of runtime problems.
    
    p.set_option("errorpolicy=exception")

    p.begin_document("invoice.pdf", "")

    p.set_info("Creator", "invoice")
    p.set_info("Author", "Thomas Merz")
    p.set_info("Title", "PDFlib invoice generation demo")

    basefontoptions = "fontname=" + fontname + " fontsize=" + \
        repr(fontsize) + " embedding encoding=unicode"

    # -----------------------------------
    # Create and place table with article list
    # -----------------------------------
    
    # ---------- Header row 
    row = 1
    col = 1
    tbl = -1; 
    for col in range(1, len(headers)+1):
        optlist =  "fittextline={position={" + alignments[col-1] + \
            " center} " + basefontoptions + "} margin=2"
        tbl = p.add_table_cell(tbl, col, row, headers[col-1], 
        optlist)

    row = row + 1

    # ---------- Data rows: one for each article 
    total = 0

    for i in range(len(dataset)): 
        sum = dataset[i][1] * dataset[i][2]
        col = 0

        # column 1: ITEM 
        buf =  "%d" % (i + 1)
        optlist = "fittextline={position={" + alignments[col] + \
            " center} " + basefontoptions + "} margin=2"
        col += 1
        tbl = p.add_table_cell(tbl, col, row, buf, optlist)

        # column 2: DESCRIPTION 
        optlist = "fittextline={position={" + alignments[col] + \
            " center} " + basefontoptions + "} colwidth=50% margin=2"
        col += 1
        tbl = p.add_table_cell(tbl, col, row, dataset[i][0],
                optlist)

        # column 3: QUANTITY 
        buf =  "%d" % dataset[i][2]
        optlist = "fittextline={position={" + alignments[col] + \
            " center} " + basefontoptions + "} margin=2"
        col += 1
        tbl = p.add_table_cell(tbl, col, row, buf, optlist)

        # column 4: PRICE 
        buf =  "%.2f" % dataset[i][1]
        optlist = "fittextline={position={" + alignments[col] + \
            " center} " + basefontoptions + "} margin=2"
        col += 1
        tbl = p.add_table_cell(tbl, col, row, buf, optlist)

        # column 5: AMOUNT 
        buf =  "%.2f" % sum
        optlist = "fittextline={position={" + alignments[col] + \
            " center} " + basefontoptions + " " + "} margin=2"
        col += 1
        tbl = p.add_table_cell(tbl, col, row, buf, optlist)

        total += sum
        row += 1

    # ---------- Print total in the rightmost column 
    buf =  "%.2f" % total
    optlist = "fittextline={position={" + \
        alignments[len(headers)-1] + " center} " + \
        basefontoptions + "} margin=2"
    tbl = p.add_table_cell(tbl, len(headers), row, buf, optlist)
    row = row + 1


    # ---------- Footer row with terms of payment 
    optlist = basefontoptions + " alignment=justify leading=120%"
    tf = p.create_textflow(closingtext, optlist)

    optlist = "rowheight=1 margin=2 margintop=" + repr(2*fontsize) + \
        " textflow=" + repr(tf) + " colspan=" + repr(len(headers))
    tbl = p.add_table_cell(tbl, 1, row, "", optlist)
    row = row + 1


    # ---------- Place the table instance(s), creating pages as required 
    result = "_boxfull"
    while (result == "_boxfull"):
        p.begin_page_ext(0, 0, "width=a4.width height=a4.height")

        pagecount = pagecount + 1;

        if (pagecount == 1):
            create_stationery(p)
            create_header(p)
            top = y_invoice - 3*fontsize
        else:
            top = y_invoice

        # Place the table on the page; Shade every other row. 
        optlist =  "header=1 fill={{area=rowodd fillcolor={gray 0.9}}} "

        result = p.fit_table(tbl,
                x_table, top, x_table+tablewidth, 20, optlist)

        if (result == "_error"): 
            raise "Couldn't place table: " + p.get_errmsg()

        p.end_page_ext("")

    p.delete_table(tbl, "")

    p.end_document("")


except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
