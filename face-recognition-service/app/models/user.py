from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    face_embeddings = db.relationship('FaceEmbedding', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class FaceEmbedding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    embedding = db.Column(db.PickleType, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class FaceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    recognized = db.Column(db.Boolean, default=False)
    confidence = db.Column(db.Float, nullable=True)
