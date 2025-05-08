# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from .models import db
from .routes import routes
from .rag_service import rag_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    migrate = Migrate(app, db)  # <--- This line integrates Flask-Migrate
    CORS(app)
    
    app.register_blueprint(routes)
    app.register_blueprint(rag_blueprint)

    return app
