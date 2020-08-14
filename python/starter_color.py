#!/usr/bin/python
# 
# Starter color:
# Demonstrate basic use of supported color spaces
#
# Apply the following color spaces to text and vector graphics:
# - Gray
# - RGB
# - CMYK
# - ICC-based gray/rgb/cmyk
# - spot(separation)
# - Lab
# - DeviceN
# - pattern
# - shadings
#
# Required software: PDFlib/PDFlib+PDI/PPS 9.1 (only for DeviceN example)
# Required data: none
#


searchpath = "../data"
outfile = "starter_color.pdf"

y = 800
x = 50
xoffset1=80
xoffset2 = 100
yoffset = 70
r = 30

from PDFlib.PDFlib import *


try:
    p = PDFlib()

    # This means that errors in function calls trigger an exception. 
    p.set_option("errorpolicy=exception SearchPath={{" + searchpath + "}} ")

    # For this important function we prefer an error return value 
    if (p.begin_document(outfile, "errorpolicy=return") == -1):
        raise Exception("Error: " + p.get_errmsg())

    p.set_info("Creator", "PDFlib starter sample")
    p.set_info("Title", "starter_color")

    # Load the font 
    font = p.load_font("Helvetica", "unicode", "")


    # Start the page 
    p.begin_page_ext(0, 0, "width=a4.width height=a4.height")

    p.setfont(font, 14)

    # -----------------------------------------------------------------
    # Use default colors
    #
    # If no special color is set the default values will be used. The
    # default values are restored at the beginning of the page. 0=black
    # in the gray color space is the default fill and stroke color in
    # many cases, as shown in our sample.
    # -----------------------------------------------------------------

    # Fill a circle with the default black fill color 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    # Output text with default black fill color 
    p.fit_textline(
      "Circle and text with default color {gray 0}", x + xoffset2, y,  "")

    p.fit_textline("1.", x + xoffset1, y,  "")


    # -----------------------------------------------------------------
    # Use the gray color space
    #
    # gray color is defined by gray values between 0=black and 1=white.
    # -----------------------------------------------------------------

    # Set the current fill color to light gray 0.5 = 50% gray.

    optlist = "fillcolor={gray 0.5}"
    p.set_graphics_option(optlist)

    # Fill a circle with the gray color defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    #  Output text with the gray color defined above 
    textbuf = "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("2.", x + xoffset1, y,  optlist)

    # -----------------------------------------------------------------
    # Use the RGB color space
    #
    # RGB color is defined by RGB triples, i.e. three values between 0
    # and 1 specifying the percentage of red, green, and blue. (0, 0,
    # 0) is black and (1, 1, 1) is white. The commonly used RGB color
    # values in the range 0-255 must be divided by 255 in order to
    # scale them to the range 0-1 as required by PDFlib.
    # -----------------------------------------------------------------

    # Set the fill color to a grass-green represented by (0.1, 0.95, 0.3)
    # which defines 10% red, 95% green, 30% blue.

    optlist = "fillcolor={rgb 0.1 0.95 0.3}"
    p.set_graphics_option(optlist)

    # Draw a circle with the current fill color defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    # Output a text line with the RGB fill color defined above 
    textbuf = "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("3.", x + xoffset1, y,  optlist)

    # -----------------------------------------------------------------
    # Use the CMYK color space
    #
    # CMYK color is defined by four CMYK values between 0 = no color
    # and 1 = full color representing cyan, magenta, yellow, and black
    # values (0, 0, 0, 0) is white and (0, 0, 0, 1) is black.
    # -----------------------------------------------------------------


    # Set the current fill color to a pale orange represented by
    # (0.1, 0.7, 0.7, 0.1) which defines 10% cyan, 70% magenta, 70% yellow,
    # and 10% black.

    optlist = "fillcolor={cmyk 0.1 0.7 0.7 0.1}"
    p.set_graphics_option(optlist)

    # Fill a circle with the current fill color defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    # Output a text line with the CMYK fill color defined above 
    textbuf = "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("4.", x + xoffset1, y,  optlist)

    # -----------------------------------------------------------------
    # Use the Lab color
    #
    # Device-independent color in the CIE L*a*b* color space is
    # specified by a luminance value in the range 0-100 and two color
    # values in the range -127 to 128. The a value contains the
    # green-red axis, while the b value contains the blue-yellow
    # axis.
    # -----------------------------------------------------------------


    # Set the current fill color to a loud blue represented by
    # (100, -127, -127).

    optlist = "fillcolor={lab 100 -127 -127}"
    p.set_graphics_option(optlist)

    # Fill a circle with the Lab fill color defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    # Output a text line with the Lab fill color defined above 
    textbuf = "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("5.", x + xoffset1, y,  optlist)

    # ---------------------------------------------------------------
    # Use ICC based color space
    #
    # ICC-based colors are specified with the help of an ICC profile.
    # ---------------------------------------------------------------

    # Set the color based on the sRGB ICC profile to a grass-green
    # represented by the RGB color values (0.1 0.95 0.3) which
    # define 10% red, 95% green, and 30% blue.
    #
    # For the sRGB profile only,  the following alternative without
    # any ICC profile handle could be used:
    #      sprintf(optlist, "fillcolor={iccbased srgb 0.1 0.95 0.3}")


    # Load the sRGB profile. sRGB is guaranteed to be always available. 
    icchandle = p.load_iccprofile("sRGB", "usage=iccbased")
    if (icchandle == -1):
        raise Exception("Error: " + PDF_get_errmsg(p))

    # You can use similar syntax for CMYK and grayscale profiles with
    # the corresponding number of four or one color values.

    optlist = "fillcolor={iccbased %d 0.1 0.95 0.3}" % icchandle
    p.set_graphics_option(optlist)

    # Fill a circle with the ICC based RGB fill color defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    # Output a text line with the ICC based RGB fill color defined above.

    textbuf = "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("6.", x + xoffset1, y,  optlist)


    # --------------------------------------------------------------------
    # Use spot (separation) color
    #
    # Spot color (separation color space) is a builtin or user-defined
    # named color with an alternate representation in one of the
    # other color spaces above this is generally used for preparing
    # documents which are intended to be printed on an offset printing
    # machine with one or more custom colors. The tint value (percentage)
    # ranges from 0=no color to 1=maximum intensity of the spot color.
    # --------------------------------------------------------------------


    # Set spot color "PANTONE 281 U" with a tint value of 1 (=100%)
    # Alternatively the following handle-based approach can be used:
    #
    #     spot = p.makespotcolor("PANTONE 281 U", 0)
    #     sprintf(optlist, "fillcolor={spot %d 1}", spot)
    #
    # See PDFlib Tutorial for defining custom spot colors.

    optlist = "fillcolor={spotname {PANTONE 281 U} 1}"
    p.set_graphics_option(optlist)

    # Fill a circle with the ICC based RGB fill color defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    textbuf = "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("7.", x + xoffset1, y,  optlist)

    # --------------------------------------------------------------------
    # Use DeviceN color
    #
    # DeviceN color spaces can use an arbitrary number of color
    # components. If these colorants are not available on the output
    # device, the colors are converted to an alternate color space
    # via a user-supplied transform function. The tint value ranges
    # from 0=no color to 1=maximum intensity.
    # --------------------------------------------------------------------

    # Set DeviceN color with colorants Magenta and Yellow with
    # alternate color space CMYK. The PostScript transform function
    # simply adds two 0 values for the Cyan and Black channels.

    devicen = p.create_devicen("names={Magenta Yellow} alternate=devicecmyk transform={{0 0 4 1 roll}}")
    optlist = "fillcolor={devicen %d 0.5 1}" % devicen
    p.set_graphics_option(optlist)

    # Fill a circle with the DeviceN fill color defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    textbuf = "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("8.", x + xoffset1, y,  optlist)


    # --------------------------------------------------------------------
    # Use Shading colorspace to draw a color gradient
    # --------------------------------------------------------------------

    # Create axial shading from red to blue 
    sh = p.shading("axial", 10, 10, 400, 300, 0, 0, 0, 0,
     "startcolor=red endcolor=blue")

    shp = p.shading_pattern(sh, "")
    optlist = "fillcolor={pattern %d}" % shp
    p.set_graphics_option(optlist)

    # Fill a circle with the shading defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()

    textbuf = "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("9.", x + xoffset1, y,  optlist)


    # --------------------------------------------------------------------
    # Use Pattern colorspace to fill objects with a geometric pattern
    # --------------------------------------------------------------------

    w = 5.0
    h = 10.0

    # Create a pattern containing geometric objects 
    pattern = p.begin_pattern_ext(w, h, "")

    # Use RGB color for the pattern 
    p.setcolor("stroke", "rgb", 0.4, 0.5, 0.2, 0)
    p.setlinewidth(w/10)

    # Set the line cap beyond the line end 
    p.set_graphics_option("linecap=2")

    # Draw the pattern objects 
    p.moveto(0, 0)
    p.lineto(w, h / 2)
    p.lineto(0, h)
    p.stroke()

    p.moveto(0, h / 2)
    p.lineto(w / 2, h / 4)
    p.stroke()

    p.moveto(w, h)
    p.lineto(w / 2, 3 * h / 4)
    p.stroke()

    p.end_pattern()

    # Now use the pattern colorspace 
    optlist ="fillcolor={pattern %d}" % pattern
    p.set_graphics_option(optlist)

    # Fill a circle with the pattern color defined above 
    y = y - yoffset
    p.circle(x,  y, r)
    p.fill()


    # Set text rendering to "fill and stroke text" to ensure that
    # patterned text remains readable.

    p.set_text_option("textrendering=2")

    textbuf =  "Circle and text with " + optlist
    p.fit_textline(textbuf, x + xoffset2, y,  "")

    # Alternatively you can set the fill color directly in the call to
    # fit_textline(). This sets the color just for a single function call.

    p.fit_textline("10.", x + xoffset1, y,  optlist)

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
