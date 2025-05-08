from flask import Blueprint, request, jsonify
import face_recognition
import numpy as np
import cv2
from io import BytesIO
import base64
import pickle
from .models import db, Face

routes = Blueprint('routes', __name__)

@routes.route("/register", methods=["POST"])
def register_face():
    data = request.json
    img_data = base64.b64decode(data["image"])
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    locations = face_recognition.face_locations(img)
    if not locations:
        return jsonify({"error": "No face found"}), 400

    encodings = face_recognition.face_encodings(img, locations)
    name = data["name"]

    for encoding in encodings:
        face = Face(name=name, encoding=pickle.dumps(encoding))
        db.session.add(face)

    db.session.commit()
    return jsonify({"message": "Face(s) registered."})


@routes.route("/recognize", methods=["POST"])
def recognize_face():
    data = request.json
    img_data = base64.b64decode(data["image"])
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    all_faces = Face.query.all()
    known_encodings = [pickle.loads(f.encoding) for f in all_faces]
    known_names = [f.name for f in all_faces]

    locations = face_recognition.face_locations(img)
    encodings = face_recognition.face_encodings(img, locations)

    results = []
    for encoding, loc in zip(encodings, locations):
        matches = face_recognition.compare_faces(known_encodings, encoding)
        name = "Unknown"
        if True in matches:
            index = matches.index(True)
            name = known_names[index]
        results.append({"name": name, "location": loc})

    return jsonify(results)
