import os
from datetime import datetime
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename

from predict import pred_landmark
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


@app.route('/predict', methods=["POST"])
def get_image():
    if 'image' not in request.files:
        return None
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        path_name = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path_name)

        result = pred_landmark(path_name)
        now = datetime.now()
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], "output_" + str(datetime.timestamp(now)) + ".jpg")
        if cv.imwrite(output_path, result):
            return send_file(output_path, mimetype='image/jpg')

    return None
