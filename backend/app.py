# import os
from flask import Flask, json, request, redirect, url_for, Response, jsonify
import jwt
from backend.ocr import OCR
from backend.food_bank_api import Food_Bank
from backend.expiry import Expiry_date

# from werkzeug.utils import secure_filename


app = Flask(__name__)
SECRET = 'mysecret'
UPLOAD_FOLDER = './data/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

@app.route("/ping")
def ping():
    return "pong"


@app.route("/login", methods=['POST'])
def login():
    if request.is_json:
        req_object = request.get_json()
        print("request: ", req_object)
        encoded = jwt.encode(req_object, SECRET, algorithm='HS256')
        print("encoded: ", encoded)
        return jsonify({"token": str(encoded,'utf-8')}), 200
    else:
        return jsonify({"status": "Failed",
                        "reason": "Not a json"}), 400


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    print('request', request.files)
    if 'bill' not in request.files:
        return jsonify({"status": "Failed",
                        "reason": "bill is not in request.files" }), 400
    file = request.files['bill']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return jsonify({"status": "Failed",
                        "reason": "No selected file"}), 400
    if file and allowed_file(file.filename):
        # call OCR method here

        # filename = secure_filename(file.filename)
        # file.save(os.path.join(UPLOAD_FOLDER, filename))
        # return redirect(url_for('uploaded_file',
        #                         filename=filename))
        return jsonify([{"milk": "5d"}, {"bread": "2d"}, {"eggs": "7d"}])
    else:
        return jsonify({"status": "Failed",
                        "reason": "File name not valid"}), 400

def caller(image):
    ocr_obj=OCR(image)
    ocr_text=ocr_obj.text()
    ocr_text=ocr_text.split("\n")
    fd=Food_Bank()
    exp=Expiry_date()
    food_dict={}
    for line in ocr_text:
        food_item=fd.get_food(line)
        expiry_days=exp.get_expiry_date(food_item)
        if expiry_days:
            food_dict[food_item]=expiry_days
    return jsonify(food_dict)

def send_recipe(ingredients):
    fd=Food_Bank()
    return fd.get_recipe(ingredients)

