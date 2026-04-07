# -*- coding: utf-8 -*-
"""
api.py
Flask API for Kira PDF processing.
Migrated from PDFlib to reportlab + pypdf.
"""

import json
import os
import traceback

from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('ENV', 'production') == 'development'

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bad_request(msg: str):
    return jsonify({'error': msg}), 400


def _server_error(exc: Exception):
    traceback.print_exc()
    return jsonify({'error': str(exc)}), 500


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def home():
    return '<h1>Kira API</h1><p>PDF processing service is running.</p>'


# ---------------------------------------------------------------------------
# Mark routes
# ---------------------------------------------------------------------------

@app.route('/supportBar', methods=['POST'])
def supportBar():
    try:
        from support_bar import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['x'], body['y'],
            body['width'], body['height'], body['percent'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/colorNames', methods=['POST'])
def colorNames():
    try:
        from color_names import make
        body = request.get_json(force=True)
        ret = make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['fsize'], body['x'], body['y'],
            body['place'], body['sideX'], body['sideY'],
        )
        return ret
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/colorsBar', methods=['POST'])
def colorsBar():
    try:
        from colors_bar import make
        body = request.get_json(force=True)
        ret = make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['intensities'], body['size'],
            body['x'], body['y'], body['place'], body['sideX'], body['sideY'],
        )
        return ret
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/cropMark', methods=['POST'])
def cropMark():
    try:
        from crop_mark import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['x_margin'], body['y_margin'],
            body['size'], body['width'], body['height'],
            body['dist_width'], body['dist_height'], body['weight'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/cropStations', methods=['POST'])
def cropStations():
    try:
        from crop_stations import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['stationsMarks'], body['size'],
            body['dist_width'], body['dist_height'], body['weight'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/registrationMark', methods=['POST'])
def registrationMark():
    try:
        from registration_mark import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['x'], body['y'],
            body['crop_size'], body['weight'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/info', methods=['POST'])
def info():
    try:
        from info import make
        body = request.get_json(force=True)
        ret = make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['info'], body['fsize'],
            body['x'], body['y'], body['place'],
            body['sideX'], body['sideY'],
        )
        return ret
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/micropoint', methods=['POST'])
def micropoint():
    try:
        from micropoint import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['colors'], body['x'], body['y'], body['size'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/rombos', methods=['POST'])
def rombos():
    try:
        from rombos import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['rombofile'], body['x'], body['y'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/circles', methods=['POST'])
def circles():
    try:
        from circles import make
        body = request.get_json(force=True)
        ret = make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['x'], body['y'], body['colors'],
            body['place'], body['sideX'], body['sideY'],
        )
        return ret
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/oneUp', methods=['POST'])
def makeOneUp():
    try:
        from one_up import make
        body = request.get_json(force=True)
        make(
            body['searchpath'],
            body['pdffile'],
            body['outfile'],
            body['client'],
            json.dumps(body['boxes']),
            body['colors'],
            json.dumps(body['info']),
            body['separationsFolder'],
            body['pathImages'],
            body['names'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/multipage', methods=['POST'])
def makeMultipage():
    try:
        from multipage import make
        body = request.get_json(force=True)
        make(
            body['searchpath'], body['pdffile'], body['outfile'],
            body['separationsFolder'], body['pathImages'], body['names'],
        )
        return 'ok'
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


@app.route('/inkCoverage', methods=['POST'])
def getInkCoverage():
    try:
        import numpy as np
        import cv2
        body  = request.get_json(force=True)
        paths = body['paths'].split(',')
        result = []
        for path in paths:
            img        = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            ink_cov    = 1 - float(np.mean(img / 255.0))
            result.append(ink_cov)
        return str(result)
    except (KeyError, TypeError) as e:
        return _bad_request(str(e))
    except Exception as e:
        return _server_error(e)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port,
            debug=app.config['DEBUG'])
