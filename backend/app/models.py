from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pickle

db = SQLAlchemy()

class Face(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    encoding = db.Column(db.LargeBinary, nullable=False)  # Store as pickled binary
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
