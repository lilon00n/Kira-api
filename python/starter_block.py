#!/usr/bin/python
# Block starter:
# Import a PDF page containing blocks and fill text and image
# blocks with some data. For each addressee of the simulated
# mailing a separate page with personalized information is
# generated.
# 
# The Textflow Blocks are processed with variable text lengths in mind:
# if a Block doesn't fully use its vertical space or requires excess
# space, the next Block is moved up or down accordingly.
#
# Required software: PPS 9
# Required data: Block PDF (template), images, font

from PDFlib.PDFlib import *
import sys, traceback


def printf(format, *args):
    sys.stdout.write(format % args)
    
# This is where the data files are. Adjust as necessary.
searchpath = "../data"
outfile = "starter_block.pdf"
infile = "block_template.pdf"

number_of_recipients = 3

# Names and contents of text Blocks

TextBlocks = []
TextBlocks = [ 
    {
        "name": "recipient",
        # address data for each recipient
        "contents": [
            "Mr Maurizio Moroni\nStrada Provinciale 124\nReggio Emilia",
            "Ms Dominique Perrier\n25, Rue Lauriston\nParis",
            "Mr Liu Wong\n55 Grizzly Peak Rd.\nButte"
          ]
    },
    {
        "name": "announcement",
        # greeting for each recipient
        "contents": [
            "Dear Paper Planes Fan,\n\n" 
            "we are happy to present our <fillcolor=red>best price offer" 
            "<fillcolor=black> especially for you:\n",
            
            "Bonjour,\n\n" 
            "here comes your personal <fillcolor=red>best price offer:\n",
            
            "Dear Paper Folder,\n\n" 
            "here's another exciting new paper plane especially for you. " 
            "We can supply this <fillcolor=red>best price offer" 
            "<fillcolor=black> only for a limited time and in limited quantity. " 
            "Don't hesitate and order your new plane today!\n",
        ]
    },
    {
        "name": "specialoffers",
        # personalized offer for each recipient
        "contents": [
            "<fillcolor=red>Long Distance Glider<fillcolor=black>\n" 
            "With this paper rocket you can send all your " 
            "messages even when sitting in a hall or in the cinema pretty near " 
            "the back.\n",
            
            "<fillcolor=red>Giant Wing<fillcolor=black>\n" 
            "An unbelievable sailplane! It is amazingly robust and " 
            "can even do aerobatics. But it is best suited to gliding.\n" 
            "This paper arrow can be thrown with big swing. " 
            "We launched it from the roof of a hotel. It stayed in the air a " 
            "long time and covered a considerable distance.\n",
            
            "<fillcolor=red>Super Dart<fillcolor=black>\n" 
            "The super dart can fly giant loops with a radius of 4 " 
            "or 5 meters and cover very long distances. Its heavy cone point is " 
            "slightly bowed upwards to get the lift required for loops.\n"
        ]
    },
    {
        "name": "goodbye",
        # bye bye phrase for each recipient
        "contents": [
            "Visit us on our Web site at <fillcolor=blue>www.kraxi.com<fillcolor=black>!\n\n" +
            "Yours sincerely,\nVictor Kraxi",
            "Make sure to order quickly at <fillcolor=blue>www.kraxi.com<fillcolor=black> " +
            "since we will soon run out of stock!\n\n" +
            "Yours sincerely,\nVictor Kraxi",

            "Make sure to order soon at <fillcolor=blue>www.kraxi.com<fillcolor=black>!\n\n" +
            "Your friendly staff at Kraxi Systems Paper Planes",
        ]
    }
]
ImageBlocks = []
ImageBlocks = [
    {
        "name": "icon",
        # image file name for each recipient
        "contents": [
            "plane1.png",
            "plane2.png",
            "plane3.png"
        ]
    }
]

p = None

try:
    p = PDFlib()

    p.set_option("SearchPath={{" + searchpath +"}}")
    # This means we must check return values of load_font() etc.
    # Set the search path for fonts and images etc.

    p.set_option("errorpolicy=return SearchPath={{" + searchpath + "}}")

    if (p.begin_document(outfile,
        "destination={type=fitwindow} pagelayout=singlepage") == -1):
            raise Exception( "Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_block")

    #  Open the Block template with PDFlib Blocks
    indoc = p.open_pdi_document(infile, "")
    if (indoc == -1):
        raise Exception( "Error: " + p.get_errmsg())
        
    no_of_input_pages = p.pcos_get_number(indoc, "length:pages")
    # Preload all pages of the Block template. We assume a small
    # number of input pages and a large number of generated output
    # pages. Therefore it makes sense to keep the input pages
    # open instead of opening them again for each recipient.
    # Add 1 because we use the 1-based page number as array index.
    pagehandles = {}

    for pageno in range(1, int(no_of_input_pages)+1):
        # Open the first page and clone the page size 
        pagehandles[pageno] = p.open_pdi_page(indoc, pageno, "cloneboxes")
        if (pagehandles[pageno] == -1):
            raise Exception( "Error: " + p.get_errmsg())
   
    # For each recipient: place template page(s) and fill Blocks
    for recipient in range(0, int(number_of_recipients-1)+1):

        # Process all pages of the template document
        for pageno in range(1, int(no_of_input_pages)+1):
            # Start the next output page. The page size will be
            # replaced with the cloned size of the input page.
            p.begin_page_ext(0, 0, "width=a4.width height=a4.height")

            # Place the imported page on the output page, and clone all
            # page boxes which are present in the input page; this will
            # override the dumsize used in begin_page_ext().
            p.fit_pdi_page(pagehandles[pageno], 0, 0, "cloneboxes")

            # Accumulated unused or excess space in Textflow Blocks
            offset_y = 0

            tf = -1
            lly = 0
            llx = 0

            # Process all Textflow Blocks
            for block in range (len(TextBlocks)):
                textflow = -1
                # The Textflow Blocks in the template use "fitmethod=nofit"
                # which means we allow the Textflow to overflow the Block.
                baseopt = "encoding=unicode embedding"
                optlist = baseopt

                # pCOS path for the current Block 
                blockpath = "pages[" + str(pageno-1) + "]/blocks/" + TextBlocks[block]["name"]
                
                # Check whether this is a Textflow Block (as opposed to Textline)
                objtype = p.pcos_get_string(indoc, "type:" + blockpath + "/textflow")
                if (objtype == "boolean" and
                    p.pcos_get_number(indoc, blockpath + "/textflow") != 0):

                    # Supplying the "textflowoption" option to fill_textblock() makes
                    # this method return a valid Textflow handle for the Block
                    # contents. We use this handle later in info_textflow()
                    # to retrieve the end position of the text.
                    textflow = 1
                    optlist += " textflowhandle=-1"

                # Retrieve coordinates of the Block's lower left corner
                llx = p.pcos_get_number(indoc, blockpath + "/Rect[0]")
                lly = p.pcos_get_number(indoc, blockpath + "/Rect[1]")

                # Adjust the vertical Block position by offset_y
                # and make sure we don't fall off the lower page edge.
                # Similarly we could adjust the horizontal position.
                lly += offset_y
                if (lly < 0):
                    raise Exception( "Error for recipient " + recipient + 
                        " (input page " +pageno + "): " +
                        "Too much text in Textflow Blocks")

                # The "refpoint" option overrides the Blocks's original
                # position. This way we can move the Block up or down
                # if the previous Blocks didn't use up their area or exceeded
                # the Block area.
                optlist += " refpoint {" + str(llx) + " " + str(lly) + "}"

                # Fill the text Block.
                # The return value is usually only an error indicator,
                # but for Textflow Blocks with "textflowhandle" it
                # returns a usable Textflow handle.

                tf = p.fill_textblock(pagehandles[pageno], TextBlocks[block]["name"],
                    TextBlocks[block]["contents"][recipient], optlist)
                
                if (tf == -1):
                    print("Warning: " + p.get_errmsg() + "\n")
                elif (textflow): 
                    # We successfully filled a Textflow Block. Retrieve
                    # vertical end position and height of the text...
                    textendy = p.info_textflow(tf, "textendy")
                    textheight = p.info_textflow(tf, "textheight")
                    p.delete_textflow(tf)

                    # +..and accumulate the Block height which wasn't used
                    # or was used in excess of the Block height.
                    # This will be used for adjusting the next Block.
                    # Don't do this for empty Textflows since info_textflow()
                    # reports textendy=0 for those.
                    offset_y += (textendy - lly )

            # Process all image Blocks
            for imageblock in ImageBlocks:
                image = p.load_image("auto", imageblock["contents"][recipient], "")
                if (image == -1):
                    raise Exception( "Error: " + p.get_errmsg())

                # Fill image Block
                if (p.fill_imageblock(pagehandles[pageno], imageblock["name"], image, "") == -1):
                    print("Warning: " + p.get_errmsg() + "\n") 
                p.close_image(image)
            p.end_page_ext("")

    # Close the preloaded template pages
    for pageno in range(1, int(no_of_input_pages)+1):
        p.close_pdi_page(pagehandles[pageno])

    p.close_pdi_document(indoc)

    p.end_document("")

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)
    traceback.print_tb()

finally:
    if p:
        p.delete()
