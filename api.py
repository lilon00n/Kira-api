
import json
from flask import Flask, request, jsonify
app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Shulian Python is working</h1><p>This API is gonna be awesome</p>"


@app.route('/pdflib', methods=['GET'])
def pdflib():
    from starter_pdfimpose import impose
    impose("starter_pdfimpose.pdf")
    return "<h1>PDFLib</h1><p>API working!</p>"


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        path = request.form['path']
        print(path)
        return "<h1>PDFLib</h1><p>Test POST working!</p>"
    else:
        return "<h1>PDFLib</h1><p>Test GET working!</p>"


@app.route('/supportBar', methods=['POST'])
def supportBar():
    from support_bar import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        colors = body["colors"]
        x = body["x"]
        y = body["y"]
        width = body["width"]
        height = body["height"]
        percent = body["percent"]
        make(searchpath, pdffile, outfile, colors, x, y, width, height, percent)
        return "ok"


@app.route('/colorNames', methods=['POST'])
def colorNames():
    from color_names import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        colors = body["colors"]
        fsize = body["fsize"]
        x = body["x"]
        y = body["y"]
        place = body["place"]
        sideX = body["sideX"]
        sideY = body["sideY"]
        ret = make(searchpath, pdffile, outfile, colors,
                   fsize, x, y, place, sideX, sideY)
        return ret


@app.route('/colorsBar', methods=['POST'])
def colorsBar():
    from colors_bar import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        colors = body["colors"]
        intensities = body["intensities"]
        x = body["x"]
        y = body["y"]
        size = body["size"]
        place = body["place"]
        sideX = body["sideX"]
        sideY = body["sideY"]
        ret = make(searchpath, pdffile, outfile, colors,
                   intensities, size, x, y, place, sideX, sideY)
        return ret


@app.route('/cropMark', methods=['POST'])
def cropMark():
    from crop_mark import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        colors = body["colors"]
        x_margin = body["x_margin"]
        y_margin = body["y_margin"]
        size = body["size"]
        width = body["width"]
        height = body["height"]
        dist_width = body["dist_width"]
        dist_height = body["dist_height"]
        weight = body["weight"]
        make(searchpath, pdffile, outfile,  colors, x_margin, y_margin,
             size, width, height, dist_width, dist_height, weight)
        return "ok"


@app.route('/cropStations', methods=['POST'])
def cropStations():
    from crop_stations import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        colors = body["colors"]
        stationsMarks = body["stationsMarks"]
        size = body["size"]
        dist_width = body["dist_width"]
        dist_height = body["dist_height"]
        weight = body["weight"]
        make(searchpath, pdffile, outfile,  colors, stationsMarks,
             size,  dist_width, dist_height, weight)
        return "ok"


@app.route('/registrationMark', methods=['POST'])
def registrationMark():
    from registration_mark import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        colors = body["colors"]
        x = body["x"]
        y = body["y"]
        crop_size = body["crop_size"]
        weight = body["weight"]

        ret = make(searchpath, pdffile, outfile,
                   colors, x, y, crop_size, weight)
        return "ok"


@app.route('/info', methods=['POST'])
def info():
    from info import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        colors = body["colors"]
        info = body["info"]
        fsize = body["fsize"]
        x = body["x"]
        y = body["y"]
        place = body["place"]
        sideX = body["sideX"]
        sideY = body["sideY"]
        ret = make(searchpath, pdffile, outfile,  colors, info,
                   fsize, x, y, place, sideX, sideY)
        return ret


@app.route('/micropoint', methods=['POST'])
def micropoint():
    from micropoint import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        colors = body["colors"]
        x = body["x"]
        y = body["y"]
        size = body["size"]
        make(searchpath, pdffile, outfile, colors, x, y, size)
        return "ok"


@app.route('/rombos', methods=['POST'])
def rombos():
    from rombos import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        rombofile = body["rombofile"]
        x = body["x"]
        y = body["y"]

        make(searchpath, pdffile, outfile, rombofile, x, y)
        return "ok"


@app.route('/oneUp', methods=['POST'])
def makeOneUp():
    from one_up import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        boxes = json.dumps(body["boxes"])
        colors = body["colors"]
        info = json.dumps(body["info"])
        make(searchpath, pdffile, outfile, boxes, colors, info)
        return "ok"


@app.route('/multipage', methods=['POST'])
def makeMultipage():
    from multipage import make
    if request.method == 'POST':
        body = request.get_json()
        searchpath = body["searchpath"]
        pdffile = body["pdffile"]
        outfile = body["outfile"]
        separationsFolder = body["separationsFolder"]
        # boxes = json.dumps(body["boxes"])
        pathImages = body["pathImages"]
        names = body["names"]
        # info = json.dumps(body["info"])
        make(searchpath, pdffile, outfile, separationsFolder, pathImages, names)
        return "ok"


@app.route('/inkCoverage', methods=['POST'])
def getInkCoverage():
    import numpy as np
    import cv2
    import sys
    print("pasé la importación")
    if request.method == 'POST':
        body = request.get_json()
        paths = body["paths"]
        print("objeto paths")
        print(paths)

        paths = paths.split(',')

        array = []
        for path in paths:
            img = cv2.imread(path, 0)

            inkcovIMG = img/np.full(img.shape, 255)
            inkCovFromImg = 1-np.mean(inkcovIMG)
            print(inkCovFromImg)
            array.append(inkCovFromImg)

        # return str(array[::-1])
        return str(array)
        # return getInkCoverageList(paths)

# print(array)

# def getInkCoverageList():
#     import numpy as np
#     import cv2
#     import sys

#     for path in paths:
#     img = cv2.imread(path, 0)

#     inkcovIMG = img/np.full(img.shape, 255)
#     inkCovFromImg = 1-np.mean(inkcovIMG)
#     print (inkCovFromImg)
#     array.append(inkCovFromImg)


app.run(host="0.0.0.0", port=8000, debug=True)
