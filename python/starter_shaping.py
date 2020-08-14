# Starter sample for text shaping features
# Demonstrate text shaping for Arabic, Hebrew, and Devanagari scripts
# Right-to-left text is reordered according to the Bidi algorithm.
#
# Required software: PDFlib/PDFlib+PDI/PPS 9
# Required data: suitable fonts for the scripts

from PDFlib.PDFlib import *

# This is where the data files are. Adjust as necessary.
searchpath = "../data"
outfile = "starter_shaping.pdf"
llx = 25.0
lly = 25.0
urx = 825.0
ury = 550.0
headers = ["Language", "Raw input", "Reordered and shaped output"]

# expects an array with 5 elements and returns a corresponding dictionary with
# the keys "fontopt", "optlist", "textflow", "language", "text"
def make_shaping_dict(x):
  assert len(x) == 5
  return dict(zip(["fontopt", "optlist", "textflow", "language", "text"], x))

shapingsamples = map(
    make_shaping_dict,
    [
        # -------------------------- Arabic -------------------------- 
        [ "fontname=NotoNaskhArabic-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=arab", 0, "Arabic",
        "&#x0627;&#x0644;&#x0639;&#x064E;&#x0631;&#x064E;&#x0628;&#x0650;"
        "&#x064A;&#x0629;" ],

        [ "fontname=NotoNaskhArabic-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=arab", 0, "Arabic",
        "&#x0645;&#x0631;&#x062D;&#x0628;&#x0627;! (Hello)"
        ],

        [ "fontname=NotoNaskhArabic-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=arab", 0, "Arabic",
        "&#xFEFF;&#x0627;&#x0644;&#x0645;&#x0627;&#x062F;&#x0629;&#x0020;"
        "&#x0031;&#x0020;&#x064A;&#x0648;&#x0644;&#x062F;&#x0020;&#x062C;"
        "&#x0645;&#x064A;&#x0639;&#x0020;&#x0627;&#x0644;&#x0646;&#x0627;"
        "&#x0633;&#x0020;&#x0623;&#x062D;&#x0631;&#x0627;&#x0631;&#x064B;"
        "&#x0627;&#x0020;&#x0645;&#x062A;&#x0633;&#x0627;&#x0648;&#x064A;"
        "&#x0646;&#x0020;&#x0641;&#x064A;&#x0020;&#x0627;&#x0644;&#x0643;"
        "&#x0631;&#x0627;&#x0645;&#x0629;&#x0020;&#x0648;&#x0627;&#x0644;"
        "&#x062D;&#x0642;&#x0648;&#x0642;&#x002E;&#x0020;"
        ],

        [ "fontname=NotoNaskhArabic-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=arab", 0, "Arabic",
        "&#x0648;&#x0642;&#x062F;&#x0020;&#x0648;&#x0647;&#x0628;&#x0648;"
        "&#x0627;&#x0020;&#x0639;&#x0642;&#x0644;&#x0627;&#x064B;&#x0020;"
        "&#x0648;&#x0636;&#x0645;&#x064A;&#x0631;&#x064B;&#x0627;&#x0020;"
        "&#x0648;&#x0639;&#x0644;&#x064A;&#x0647;&#x0645;&#x0020;&#x0623;"
        "&#x0646;&#x0020;&#x064A;&#x0639;&#x0627;&#x0645;&#x0644;&#x0020;"
        "&#x0628;&#x0639;&#x0636;&#x0647;&#x0645;&#x0020;&#x0628;&#x0639;"
        "&#x0636;&#x064B;&#x0627;&#x0020;&#x0628;&#x0631;&#x0648;&#x062D;"
        "&#x0020;&#x0627;&#x0644;&#x0625;&#x062E;&#x0627;&#x0621;&#x002E;"
        ],

        # -------------------------- Hebrew --------------------------
        [ "fontname=NotoSerifHebrew-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=hebr", 0, "Hebrew",
          "&#x05E2;&#x05B4;&#x05D1;&#x05B0;&#x05E8;&#x05B4;&#x05D9;&#x05EA;"
        ],

        [ "fontname=NotoSerifHebrew-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=hebr", 0, "Hebrew",
        "&#x05E1;&#x05E2;&#x05D9;&#x05E3;&#x0020;&#x05D0;&#x002E;&#x0020;"
        "&#x05DB;&#x05DC;&#x0020;&#x05D1;&#x05E0;&#x05D9;&#x0020;&#x05D0;"
        "&#x05D3;&#x05DD;&#x0020;&#x05E0;&#x05D5;&#x05DC;&#x05D3;&#x05D5;"
        "&#x0020;&#x05D1;&#x05E0;&#x05D9;&#x0020;&#x05D7;&#x05D5;&#x05E8;"
        "&#x05D9;&#x05DF;&#x0020;&#x05D5;&#x05E9;&#x05D5;&#x05D5;&#x05D9;"
        "&#x05DD;&#x0020;&#x05D1;&#x05E2;&#x05E8;&#x05DB;&#x05DD;&#x0020;"
        "&#x05D5;&#x05D1;&#x05D6;&#x05DB;&#x05D5;&#x05D9;&#x05D5;&#x05EA;"
        "&#x05D9;&#x05D4;&#x05DD;&#x002E;&#x0020;"
        ],

        [ "fontname=NotoSerifHebrew-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=hebr", 0, "Hebrew",
        "&#x05DB;&#x05D5;&#x05DC;&#x05DD;&#x0020;&#x05D7;&#x05D5;&#x05E0;"
        "&#x05E0;&#x05D5;&#x0020;&#x05D1;&#x05EA;&#x05D1;&#x05D5;&#x05E0;"
        "&#x05D4;&#x0020;&#x05D5;&#x05D1;&#x05DE;&#x05E6;&#x05E4;&#x05D5;"
        "&#x05DF;&#x002C;&#x0020;"
        ],

        [ "fontname=NotoSerifHebrew-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=hebr", 0, "Hebrew",
        "&#x05DC;&#x05E4;&#x05D9;&#x05DB;&#x05DA;&#x0020;&#x05D7;&#x05D5;"
        "&#x05D1;&#x05D4;&#x0020;&#x05E2;&#x05DC;&#x05D9;&#x05D4;&#x05DD;"
        "&#x0020;&#x05DC;&#x05E0;&#x05D4;&#x05D5;&#x05D2;&#x0020;&#x05D0;"
        "&#x05D9;&#x05E9;&#x0020;&#x05D1;&#x05E8;&#x05E2;&#x05D4;&#x05D5;"
        "&#x0020;&#x05D1;&#x05E8;&#x05D5;&#x05D7;&#x0020;&#x05E9;&#x05DC;"
        "&#x0020;&#x05D0;&#x05D7;&#x05D5;&#x05D4;&#x002E;"
        ],

        # -------------------------- Hindi -------------------------- 
        [ "fontname=NotoSerifDevanagari-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=deva", 1, "Hindi",
          "&#x0939;&#x093F;&#x0928;&#x094D;&#x0926;&#x0940;"
        ],

        [ "fontname=NotoSerifDevanagari-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=deva advancedlinebreak", 1, "Hindi",
        "&#x0905;&#x0928;&#x0941;&#x091A;&#x094D;&#x091B;&#x0947;&#x0926;"
        "&#x0020;&#x0967;&#x002E;&#x0020;&#x0938;&#x092D;&#x0940;&#x0020;"
        "&#x092E;&#x0928;&#x0941;&#x0937;&#x094D;&#x092F;&#x094B;&#x0902;"
        "&#x0020;&#x0915;&#x094B;&#x0020;&#x0917;&#x094C;&#x0930;&#x0935;"
        "&#x0020;&#x0914;&#x0930;&#x0020;&#x0905;&#x0927;&#x093F;&#x0915;"
        "&#x093E;&#x0930;&#x094B;&#x0902;&#x0020;&#x0915;&#x0947;&#x0020;"
        "&#x092E;&#x093E;&#x092E;&#x0932;&#x0947;&#x0020;&#x092E;&#x0947;"
        "&#x0902;&#x0020;&#x091C;&#x0928;&#x094D;&#x092E;&#x091C;&#x093E;"
        "&#x0924;&#x0020;&#x0938;&#x094D;&#x0935;&#x0924;&#x0928;&#x094D;"
        "&#x0924;&#x094D;&#x0930;&#x0924;&#x093E;&#x0020;&#x0914;&#x0930;"
        "&#x0020;&#x0938;&#x092E;&#x093E;&#x0928;&#x0924;&#x093E;&#x0020;"
        "&#x092A;&#x094D;&#x0930;&#x093E;&#x092A;&#x094D;&#x0924;&#x0020;"
        "&#x0939;&#x0948;&#x0020;&#x0964;&#x0020;&#x0909;&#x0928;&#x094D;"
        "&#x0939;&#x0947;&#x0902;&#x0020;&#x092C;&#x0941;&#x0926;&#x094D;"
        "&#x0918;&#x093F;&#x0020;&#x0914;&#x0930;&#x0020;&#x0905;&#x0928;"
        "&#x094D;&#x0924;&#x0930;&#x093E;&#x0924;&#x094D;&#x092E;&#x093E;"
        "&#x0020;&#x0915;&#x0940;&#x0020;&#x0926;&#x0947;&#x0928;&#x0020;"
        "&#x092A;&#x094D;&#x0930;&#x093E;&#x092A;&#x094D;&#x0924;&#x0020;"
        "&#x0939;&#x0948;&#x0020;&#x0914;&#x0930;&#x0020;&#x092A;&#x0930;"
        "&#x0938;&#x094D;&#x092A;&#x0930;&#x0020;&#x0909;&#x0928;&#x094D;"
        "&#x0939;&#x0947;&#x0902;&#x0020;&#x092D;&#x093E;&#x0908;&#x091A;"
        "&#x093E;&#x0930;&#x0947;&#x0020;&#x0915;&#x0947;&#x0020;&#x092D;"
        "&#x093E;&#x0935;&#x0020;&#x0938;&#x0947;&#x0020;&#x092C;&#x0930;"
        "&#x094D;&#x0924;&#x093E;&#x0935;&#x0020;&#x0915;&#x0930;&#x0928;"
        "&#x093E;&#x0020;&#x091A;&#x093E;&#x0939;&#x093F;&#x090F;&#x0020;"
        "&#x0964;"
        ],

        # -------------------------- Sanskrit --------------------------
        [ "fontname=NotoSerifDevanagari-Regular encoding=unicode fallbackfonts={ {fontname=NotoSerif-Regular encoding=unicode} }", "shaping script=deva", 1, "Sanskrit",
        "&#x0938;&#x0902;&#x0938;&#x094D;&#x0915;&#x0943;&#x0924;&#x092E;"
        "&#x094D;"
    ]
        ]
)

p = None

try:
    p = PDFlib()

    p.set_option("SearchPath={{" + searchpath +"}}")

    # This means that formatting and other errors will raise an
    # exception. This simplifies our sample code, but is not
    # recommended for production code.
    p.set_option("errorpolicy=exception")
    p.set_option("charref=true");

    # Set an output path according to the name of the topic
    if (p.begin_document(outfile, "") == -1):
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_shaping")

    table = -1

    # Create table header
    row = 1
    col = 1
    for header in headers:
        if (col == 1):
            percentage = "10%"
        else:
            percentage = "45%"
        optlist = (
           "fittextline={fontname=NotoSerif-Regular encoding=unicode fontsize=14} "
           "colwidth=" + percentage )
        table = p.add_table_cell(table, col, row, header, optlist)
        col += 1
        
    row += 1
    
    # Create shaping samples
    for shapingsample in shapingsamples:
        col=1

        # Column 1: language name
        optlist = "fittextline={fontname=NotoSerif-Regular encoding=unicode fontsize=12}"
        table = p.add_table_cell(table, col, row, shapingsample["language"], optlist)

        col += 1

        # Column 2: raw text
        optlist = (
            "%s fontsize=12 leading=150%% alignment=left" %
                shapingsample["fontopt"])
        tf = p.create_textflow(shapingsample["text"],optlist)
        optlist = "margin=4 fittextflow={verticalalign=top} textflow=%d" % tf
        table = p.add_table_cell(table, col, row, "", optlist)

        col += 1
        
        # Column 3: shaped and reordered text (Textline or Textflow)
        if (shapingsample["textflow"]):
            optlist = (
               "%s %s fontsize=12 leading=150%% alignment=left" %
                   (shapingsample["fontopt"], shapingsample["optlist"]))
            tf = p.create_textflow(shapingsample["text"], optlist)
            optlist = "margin=4 fittextflow={verticalalign=top} textflow=%d" % tf
            table = p.add_table_cell(table, col, row, "", optlist)
        else:
            optlist = (
               "fittextline={%s %s fontsize=12}" %
                   (shapingsample["fontopt"], shapingsample["optlist"]))
            table = p.add_table_cell(table, col, row,
                     shapingsample["text"], optlist)
            
        row += 1

    # ---------- Place the table on one or more pages ----------
    #
    # Loop until all of the table is placed; create new pages
    # as long as more table instances need to be placed.
    result = "_boxfull"
    while (result == "_boxfull"):
        p.begin_page_ext(0, 0, "width=a4.height height=a4.width")

        # Shade every other row; draw lines for all table cells.
        optlist = "header=1 fill={{area=rowodd fillcolor={gray 0.9}}} stroke={{line=other}} "

        # Place the table instance
        result = p.fit_table(table, llx, lly, urx, ury, optlist)

        if (result == "_error"):
            raise Exception("Couldn't place table: " + p.get_errmsg())

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
