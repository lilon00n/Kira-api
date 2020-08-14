# PDF/A-2b starter:
# Create PDF/A-2b conforming output with layers, transparency and
# PDF/A attachments.
#
# Required software: PDFlib/PDFlib+PDI/PPS 9
# Required data: font file, image file, ICC output intent profile
#                (see www.pdflib.com for output intent ICC profiles)

from PDFlib.PDFlib import *

# This is where the data files are. Adjust as necessary.
searchpath = "../data"
imagefile = "zebra.tif"
attachments = [ "lionel.pdf"]

p = None

try:
    p = PDFlib()

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return")

    p.set_option("SearchPath={{" + searchpath +"}}")

    # Initially display the layer panel and show the full page
    if (p.begin_document("starter_pdfa2b.pdf",
         "openmode=layers viewerpreferences={fitwindow=true} " + 
         "pdfa=PDF/A-2b") == -1):
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_pdfa2b")

    if (p.load_iccprofile("sRGB", "usage=outputintent") == -1):
        raise Exception("Error: " + p.get_errmsg() + "\n" +
            "See www.pdflib.com for output intent ICC profiles.") 

    # Define the layers, with only English and image layers switched on.
    layer_english = p.define_layer("English text", "")
    layer_german  = p.define_layer("German text", "defaultstate=false")
    layer_french  = p.define_layer("French text", "defaultstate=false")
    layer_image   = p.define_layer("Images", "")

    # Define a radio button relationship for the language layers, so only
    # one language can be switched on at a time.
    optlist = ("group={%d %d %d}" %
            (layer_english, layer_german, layer_french))
    p.set_layer_dependency("Radiobtn", optlist);

    p.begin_page_ext(0,0, "width=a4.width height=a4.height")

    # Font embedding is required for PDF/A
    font = p.load_font("NotoSerif-Regular", "winansi", "embedding")

    if (font == -1):
        raise Exception("Error: " + p.get_errmsg())

    optlist = "font=%d fontsize=24" % font

    p.begin_layer(layer_english)
    textflow = p.create_textflow(
                "PDF/A-2b starter sample with layers, transparency " +
                "and attachments", optlist)
    p.fit_textflow(textflow, 50, 650, 550, 700, "")
    p.delete_textflow(textflow)

    p.begin_layer(layer_german)
    textflow = p.create_textflow(
                "PDF/A-2b Starter-Beispiel mit Ebenen, Transparenz " +
                "und Anlagen", optlist)
    p.fit_textflow(textflow, 50, 650, 550, 700, "")
    p.delete_textflow(textflow)

    p.begin_layer(layer_french)
    textflow = p.create_textflow(
                "PDF/A-2b starter exemple avec des calques, " +
                "de la transparence et des annexes", optlist)
    p.fit_textflow(textflow, 50, 650, 550, 700, "")
    p.delete_textflow(textflow)

    p.begin_layer(layer_image)

    p.setfont(font, 48)

    image = p.load_image("auto", imagefile, "")

    if (image == -1):
        raise Exception("Error: " + p.get_errmsg())
        
    width = p.info_image(image, "width", "")
    height = p.info_image(image, "height", "")
    
    # Place the image on the page and close it
    p.fit_image(image, 0.0, 0.0, "")
    p.close_image(image)

    # Set transparency in the graphics state
    gstate = p.create_gstate("opacityfill=0.5")
    p.set_gstate(gstate)

    # Place a transparent diagonal stamp across the image area, in
    # different colors
    optlist = "boxsize={%f %f} stamp=ll2ur" % (width, height)
    
    p.begin_layer(layer_english);
    p.setcolor("fill", "Lab", 100, 28, 75, 0);
    p.fit_textline("Transparent text", 0, 0, optlist);

    p.begin_layer(layer_german);
    p.setcolor("fill", "Lab", 33.725, 5, -52, 0);
    p.fit_textline("Transparenter Text", 0, 0, optlist);

    p.begin_layer(layer_french);
    p.setcolor("fill", "Lab", 0, 0, 0, 0);
    p.fit_textline("Texte transparent", 0, 0, optlist);

    # Close all layers
    p.end_layer()

    p.end_page_ext("")
    
    # Construct option list with attachment handles. The attachments must
    # be PDF/A-1 or PDF/A-2 files.
    optlist = "attachments={"
    for attachment in attachments:
        attachment_handle = p.load_asset("Attachment", attachment,
                                  "description={This is a PDF/A attachment}")

        if (attachment_handle == -1):
            raise Exception("Error loading attachment: " + p.get_errmsg())

        optlist += " %d" % attachment_handle
    
    optlist += "}"
    
    p.end_document(optlist)

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
