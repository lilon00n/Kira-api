# 
# Starter sample for path objects:
# Create some basic examples of path object construction and use
#
# Required software: PDFlib/PDFlib+PDI/PPS 9
# Required data: none
#

from PDFlib.PDFlib import *

# This is where the data files are. Adjust as necessary.
outfile = "starter_path.pdf"

p = None

try:
    p = PDFlib()
    
    text= \
"Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. "

    # This means we must check return values of load_font() etc.
    p.set_option("errorpolicy=return")

    if (p.begin_document(outfile, "") == -1):
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_path")

    # Start an A4 page
    p.begin_page_ext(0, 0, "width=a4.width height=a4.height")

    # Construct a path object for an arrow shape

    path = -1

    # The tip of the arrow gets rounded corners
    path = p.add_path_point(path, 200.0,  25.0, "move", "round=10")
    path = p.add_path_point(path, 200.0,  75.0, "line", "")
    # assign a name to the arrow's tip
    path = p.add_path_point(path, 300.0,   0.0, "line", "name=tip")
    path = p.add_path_point(path, 200.0, -75.0, "line", "")
    path = p.add_path_point(path, 200.0, -25.0, "line", "")

    # Start a new subpath for the straight base of the arrow
    path = p.add_path_point(path, 200.0, -25.0, "move", "")
    path = p.add_path_point(path,   0.0, -25.0, "line", "")

    # The center of the base can serve as a named attachment point
    path = p.add_path_point(path,   0.0,   0.0, "line", "name=base")
    path = p.add_path_point(path,   0.0,  25.0, "line", "")
    path = p.add_path_point(path, 200.0,  25.0, "line", "")

    x = 100.0
    y = 850.0

    # ----------------------------------------
    # Place arrow in its original direction
    # ----------------------------------------
    y -= 100.0
    p.draw_path(path, x, y,
        "stroke linewidth=3 fill fillcolor=Turquoise "
        "linecap=projecting attachmentpoint=base ")

    # ----------------------------------------
    # Scale down arrow and align it to north east
    # ----------------------------------------
    y -= 200.0
    p.draw_path(path, x, y,
        "stroke linewidth=3 fill fillcolor=Turquoise "
        "linecap=projecting attachmentpoint=base scale=0.5 align={1 1}")

    # ----------------------------------------
    # Scale to 50%, use the arrow tip as attachment point,
    # and align the arrow to the left
    # ----------------------------------------
    y -= 100.0
    p.draw_path(path, x, y,
        "stroke linewidth=3 fill fillcolor=Turquoise "
        "linecap=projecting attachmentpoint=tip scale=0.5 align={-1 0}")

    # ----------------------------------------
    # Place text on the path; round all corners to
    # allow smoother text at the corners
    # ----------------------------------------
    y -= 100.0
    optlist = ("textpath={path=%d round=10} position={center bottom} "
                "fontname=Helvetica encoding=winansi fontsize=8" %
                (path))
    p.fit_textline(text, x, y, optlist)

    # ----------------------------------------
    # Use the path as clipping path for a Textflow
    # ----------------------------------------
    y -= 300.0

    # Feed the text to the Textflow object
    tf = p.add_textflow(-1, text,
        "fontname=Helvetica fontsize=10 encoding=winansi "
        "alignment=justify")
    # Use text twice to fill the arrow
    tf = p.add_textflow(tf, text,
        "fontname=Helvetica fontsize=10 encoding=winansi "
        "alignment=justify")
    if (tf == -1):
        raise Exception("Error: " + p.get_errmsg())

    # Attach the path's reference point to the middle left (0%, 50%)
    # of the fitbox, and wrap the text inside the path (inversefill)
    
    optlist = ("wrap={inversefill "
                "paths={{path=%d refpoint={0%% 50%%} scale=1.5 }}}" %
                    (path))
    result = p.fit_textflow(tf, x, y, x+450, y+225, optlist)

    if (result == "_stop"):
        # In this example we don't care about overflow text
        pass

    p.delete_textflow(tf)

    # ----------------------------------------
    # Query information about the path object
    # ----------------------------------------
    n = p.info_path(path, "numpoints", "")

    p.delete_path(path)
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
