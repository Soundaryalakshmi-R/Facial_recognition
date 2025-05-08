import face_recognition
import numpy as np
import cv2
from app import db
from app.models.user import User, FaceEmbedding, FaceLog

class FaceService:
    def __init__(self):
        self.detection_method = 'hog'  # 'hog' is faster, 'cnn' is more accurate but requires GPU
        self.tolerance = 0.6  # Lower tolerance means stricter matching
    
    def register_face(self, image_data, user_id):
        """Register a face for a user"""
        # Convert image data to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_img, model=self.detection_method)
        if not face_locations:
            return {"success": False, "message": "No face detected"}
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        # Store face encodings
        for encoding in face_encodings:
            face_embedding = FaceEmbedding(embedding=encoding, user_id=user_id)
            db.session.add(face_embedding)
        
        db.session.commit()
        return {"success": True, "message": f"Registered {len(face_encodings)} face(s)"}
    
    def recognize_faces(self, image_data):
        """Recognize faces in image"""
        # Convert image to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_img, model=self.detection_method)
        if not face_locations:
            return {"success": False, "message": "No faces detected", "faces": []}
        
        # Get face encodings
        unknown_encodings = face_recognition.face_encodings(rgb_img, face_locations)
        
        # Get all face embeddings from database
        all_users = User.query.all()
        all_embeddings = FaceEmbedding.query.all()
        
        recognized_faces = []
        
        for i, unknown_encoding in enumerate(unknown_encodings):
            face_result = {
                "location": face_locations[i],
                "recognized": False,
                "user_info": None,
                "confidence": 0.0
            }
            
            best_match = None
            best_confidence = 0.0
            
            # Compare with stored embeddings
            for embedding in all_embeddings:
                known_encoding = embedding.embedding
                face_distances = face_recognition.face_distance([known_encoding], unknown_encoding)
                confidence = 1 - min(face_distances)
                
                if confidence > best_confidence and confidence > (1 - self.tolerance):
                    best_confidence = confidence
                    user = next((u for u in all_users if u.id == embedding.user_id), None)
                    best_match = user
            
            if best_match:
                face_result["recognized"] = True
                face_result["user_info"] = {"id": best_match.id, "username": best_match.username}
                face_result["confidence"] = best_confidence
                
                # Log this recognition
                log = FaceLog(user_id=best_match.id, recognized=True, confidence=best_confidence)
                db.session.add(log)
            
            recognized_faces.append(face_result)
        
        db.session.commit()
        return {"success": True, "faces": recognized_faces}
