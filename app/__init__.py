from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    db.init_app(app)


    from app.auth import auth_bp as auth_routes
    from app.mcq import mcq as mcq_routes

    app.register_blueprint(auth_routes, url_prefix='/auth')
    app.register_blueprint(mcq_routes, url_prefix='/mcq')

    return app