from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from app.config import Config

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    
    CORS(app)
    mongo.init_app(app)
    
    
    from app.routes.page_routes import pages_bp
    app.register_blueprint(pages_bp)
    
    return app