import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Example with SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
