from flask import Blueprint, request, jsonify
from .models import Face
from datetime import datetime

rag_blueprint = Blueprint('rag_service', __name__)

@rag_blueprint.route('/chat', methods=["POST"])
def chat():
    query = request.json.get("query", "").lower()

    if "last registered" in query:
        latest = Face.query.order_by(Face.timestamp.desc()).first()
        if latest:
            return jsonify({"response": f"{latest.name} was last registered at {latest.timestamp}"})
        else:
            return jsonify({"response": "No faces registered yet."})

    elif "who is registered" in query:
        names = [face.name for face in Face.query.all()]
        return jsonify({"response": f"Registered users: {', '.join(names)}"})

    else:
        return jsonify({"response": "I didn't understand that. Try asking about registrations."})
