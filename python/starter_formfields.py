#!/usr/bin/python
#
# formfields starter:
# create a linearized PDF (for fast delivery over the Web, also known
# as "fast Web view") which is encrypted and contains some form fields.
# A few lines of JavaScript are inserted as "page open" action to
# automatically populate the date field with the current date.
#
# required software: PDFlib/PDFlib+PDI/PPS 9
# required data: font file

from PDFlib.PDFlib import *

# This is where the data files are. Adjust as necessary. 
searchpath = "../data";

outfilename = "starter_formfields.pdf"

llx=150; lly=550; urx=350; ury=575

# JavaScript for automatically filling the date into a form field
js = "var d = util.printd(\"mm/dd/yyyy\", new Date());" \
    "var date = this.getField(\"date\");" \
    "date.value = d;"

p = None

try:
    p = PDFlib()

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return searchpath={{" + searchpath +"}}")

    # Prevent changes with a master password
    optlist = "linearize masterpassword=pdflib permissions={nomodify}"

    if (p.begin_document(outfilename, optlist) == -1):
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_formfields")

    optlist = "script[" + repr(len(js)) + "]={" + js + "}"
    action = p.create_action("JavaScript", optlist)

    optlist = "width=a4.width height=a4.height action={open=" + repr(action) + "}"
    p.begin_page_ext(0, 0, optlist)

    font = p.load_font("NotoSerif-Regular", "winansi", "simplefont embedding nosubsetting")
    if font == -1:
        raise Exception("Error: " + p.get_errmsg() + "\n")

    p.setfont(font, 24)

    p.fit_textline("Date: ", 125, lly+5, "position={right bottom}")

    # The tooltip will be used as rollover text for the field
    optlist = \
        "tooltip={Date (will be filled automatically)} " \
        "bordercolor={gray 0} font=" + repr(font)
    p.create_field(llx, lly, urx, ury, "date", "textfield", optlist)

    lly-=100; ury-=100
    p.fit_textline("Name: ", 125, lly+5, "position={right bottom}")

    optlist = "tooltip={Enter your name here} bordercolor={gray 0} font=" + repr(font)
    p.create_field(llx, lly, urx, ury, "name", "textfield", optlist)

    p.end_page_ext("")

    p.end_document("")

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
