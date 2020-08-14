# PDF portfolio starter:
# Package multiple PDF and other documents into a PDF portfolio
# The generated PDF portfolio requires Acrobat 9 for proper
# viewing. The documents in the Portfolio will be assigned predefined
# and custom metadata fields; for the custom fields a schema description
# is created.
#
# Acrobat 8 will only display a "PDF package" with a flat list of documents
# without any folder structure.
#
# Required software: PDFlib/PDFlib+PDI/PPS 9
# Required data: PDF and other input documents

from PDFlib.PDFlib import *

# This is where the data files are. Adjust as necessary.
searchpath = "../data"

# expects an array with 4 elements and returns a corresponding dictionary with
# the keys "filename", "description", "status", "id"
def make_file_dict(x):
  assert len(x) == 4
  return dict(zip(["filename", "description", "status", "id"], x))

# The documents for the Portfolio along with description and metadata
root_folder_files = map(
  make_file_dict, 
  [
      [
          "nesrin.jpg",
          "Zabrisky point",
          "archived",
          300
      ]
  ]
)

datasheet_files = map(
  make_file_dict,
  [
      [
                "PDFlib-datasheet.pdf",
                "Generate PDF on the fly",
                "published",
                101
      ],
      [
                "PLOP-datasheet.pdf",
                "PDF Linearization, Optimization, Protection",
                "published",
                103
      ],
      [
                "pCOS-datasheet.pdf",
                "PDF Information Retrieval Tool",
                "published",
                104
      ]
  ]
)

p = None

try:
    p = PDFlib()

    p.set_option("SearchPath={{" + searchpath +"}}")

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return")

    if (p.begin_document("starter_portfolio.pdf", "compatibility=1.7ext3") == -1):
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_portfolio")

    # Insert all files for the root folder along with their description
    # and the following custom fields:
    # status   string describing the document status
    # id       numerical identifier, prefixed with "PHX"
    for file in root_folder_files:
        optlist = (
            "description={%s} "
            "fieldlist={ "
                    "{key=status value=%s} "
                    "{key=id value=%d prefix=PHX type=text} "
            "}" %
            (file["description"], file["status"], file["id"]))

        # -1 means root folder
        p.add_portfolio_file(-1, file["filename"], optlist)

    # Create the "datasheets" folder in the root folder
    folder = p.add_portfolio_folder(-1, "datasheets", "")

    # Insert documents in the "datasheets" folder along with
    # description and custom fields
    for file in datasheet_files:
        optlist = (
                        "description={%s} "
                        "fieldlist={ "
                                "{key=status value=%s} "
                                "{key=id value=%d prefix=PHX type=text} "
                        "}" %
                        (file["description"], file["status"], file["id"]))
  
        # Add the file to the "datasheets" folder
        p.add_portfolio_file(folder, file["filename"], optlist)

        # Create a single-page document as cover sheet
    p.begin_page_ext(0, 0, "width=a4.width height=a4.height")

    font = p.load_font("Helvetica", "unicode", "")
    if (font == -1):
        raise Exception("Error: " + p.get_errmsg())

    p.setfont(font, 24)
    p.fit_textline("Welcome to the PDFlib Portfolio sample!", 50, 700, "")

    p.end_page_ext("")

        # Set options for Portfolio display
    optlist = (
      "portfolio={initialview=detail "
      
        # Add schema definition for Portfolio metadata
        "schema={ "
        # Some predefined fields are included here to make them visible.
        "{order=1 label=Name key=_filename visible editable} "
        "{order=2 label=Description key=_description visible} "
        "{order=3 label=Size key=_size visible} "
        "{order=4 label={Last edited} key=_moddate visible} "
      
        # User-defined fields
        "{order=5 label=Status key=status type=text editable} "
        "{order=6 label=ID key=id type=text editable} "
      "}}")
  
    p.end_document(optlist)

except PDFlibException as ex:
    print("PDFlib exception occurred:")
    print("[%d] %s: %s" % (ex.errnum, ex.apiname, ex.errmsg))

except Exception as ex:
    print(ex)

finally:
    if p:
        p.delete()
