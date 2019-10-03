import os
from datetime import datetime
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename

from predict import predict
import cv2 as cv

from flask_cors import CORS

UPLOAD_FOLDER = "./uploads"
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
OUTPUT_FOLDER = "./result"

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


temp_angle = None


@app.route('/get_image', methods=["POST"])
def get_image():
    if 'image' not in request.files:
        return None
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path_name)

        angle, masked_img = predict(path_name)

        if angle:
            global temp_angle
            temp_angle = angle

        now = datetime.now()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], "output_" + str(datetime.timestamp(now)) + ".jpg")
        if cv.imwrite(output_path, masked_img):
            return send_file(output_path, mimetype='image/jpg')

    return None


@app.route('/get_angle', methods=['GET'])
def get_angle():
    resp = {
        "angle": temp_angle[2],
        "vertebras": "{} {}".format(temp_angle[0], temp_angle[1])
    }
    return jsonify(resp)
