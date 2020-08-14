import flask

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Shulian Python is working</h1><p>This API is gonna be awesome</p>"

@app.route('/pdflib', methods=['GET'])
def pdflib():
    import starter_pdfimpose
    return "<h1>PDFLib</h1><p>API working!</p>"

app.run(host="0.0.0.0", port=8000, debug=True)
