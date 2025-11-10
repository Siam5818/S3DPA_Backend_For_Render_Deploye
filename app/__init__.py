# Initialisation Flask

import os
from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from flask_cors import CORS
from .extension import db
from app.extension import init_extension
from app.routes import register_routes

def create_app():
    app = Flask(__name__)
    
    # Enable CORS for the app
    CORS(
        app,
        resources={r"/v1/*": {"origins": "http://localhost:4200"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )


    # Load configuration based on the environment
    if os.getenv('FLASK_ENV') == 'development':
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(ProductionConfig)

    # Initialize extensions
    init_extension(app)

    # Register blueprints or routes here if needed
    register_routes(app)
    
    return app