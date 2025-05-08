from flask import Blueprint, request, jsonify
from app.services.face_service import FaceService
from app import db
from app.models.user import User

face_bp = Blueprint('face', __name__)
face_service = FaceService()

@face_bp.route('/register', methods=['POST'])
def register_face():
    if 'user_id' not in request.form or 'image' not in request.files:
        return jsonify({"success": False, "message": "User ID and image required"}), 400
    
    user_id = request.form['user_id']
    image_file = request.files['image']
    
    result = face_service.register_face(image_file.read(), user_id)
    return jsonify(result)

@face_bp.route('/recognize', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return jsonify({"success": False, "message": "Image required"}), 400
    
    image_file = request.files['image']
    result = face_service.recognize_faces(image_file.read())
    return jsonify(result)

@face_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({"success": False, "message": "Username and email required"}), 400
    
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"success": True, "user_id": user.id})
