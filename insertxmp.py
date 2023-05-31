# PDFlib PLOP: PDF Linearization, Optimization, Protection
# mini sample for inserting XMP metadata in PDF documents

# Option list for the generated output document.
# Some alternatives for the option list using the supplied XMP samples:
#
# Insert custom metadata for the GWG (Ghent Workgroup)
# Ad Ticket scheme (see http://www.gwg.org/Jobtickets.phtml):
# "metadata={filename=gwg_ad_ticket.xmp validate=xmp2004}"
#
# Insert custom metadata based on Acme's enterprise schema:
# "metadata={filename=acme.xmp}"
#
# Insert a custom "engineering" schema for scanned documents:
# This works best with a PDF/A-1 input document (e.g. mini_pdfa1.pdf),
# and requires XMP input which conforms to PDF/A-1:
# "metadata={filename=engineering.xmp}"
#
# Insert a PDF/A extension schema after validating the XMP for PDF/A-1.
# This works best with a PDF/A-1 input document (e.g. mini_pdfa1.pdf),
# and requires XMP input which conforms to PDF/A-1:
# "metadata={filename=machine_pdfa1.xmp validate=pdfa1}"
#

base_opts = "metadata={filename=gwg_ad_ticket.xmp} "

from PDFlib.PDFlib import *

# Directory where files will be searched
searchpath = "./data"
# input document
in_filename  = "PLOP-datasheet.pdf"
# output document
out_filename = "PLOP-datasheet-xmp.pdf"


plop = None
try:
    # create a new PLOP object
    plop = PLOP()

    optlist = "searchpath={%s}" % searchpath
    plop.set_option(optlist)

    # open input file
    doc = plop.open_document(in_filename, "")
    if (doc == -1):
        raise Exception("Error: %s" % plop.get_errmsg())

    # create the output file and add XMP metadata
    optlist = "%s input=%d" % (base_opts, doc)

    if (plop.create_document(out_filename, optlist) == -1):
        raise Exception("Error: %s" % plop.get_errmsg())

    # close input and output files
    plop.close_document(doc, "")

except PLOPException as ex:
    print("PDFlib PLOP exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if plop:
        plop.delete()
