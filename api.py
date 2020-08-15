
from flask import Flask, request
app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Shulian Python is working</h1><p>This API is gonna be awesome</p>"

@app.route('/pdflib', methods=['GET'])
def pdflib():
    from  starter_pdfimpose import impose
    impose("starter_pdfimpose.pdf")
    return "<h1>PDFLib</h1><p>API working!</p>"

@app.route('/test', methods=['GET','POST'])
def test():
    if request.method == 'POST':
        path = request.form['path']
        print(path)
        return "<h1>PDFLib</h1><p>Test POST working!</p>"
    else:
        return "<h1>PDFLib</h1><p>Test GET working!</p>"

@app.route('/supportBar', methods=['POST'])
def supportBar():
    from  support_bar import make
    if request.method == 'POST':
        searchpath= request.form["searchpath"]
        pdffile= request.form["pdffile"]
        outfile= request.form["outfile"] 
        x= request.form["x"]
        y= request.form["y"] 
        width= request.form["width"]
        height= request.form["height"]
        make(searchpath, pdffile, outfile, x, y, width, height)
        return "<h1>PDFLib</h1><p>Test POST working!</p>"
    else:
        return "<h1>PDFLib</h1><p>Test GET working!</p>"
app.run(host="0.0.0.0", port=8000, debug=True)
