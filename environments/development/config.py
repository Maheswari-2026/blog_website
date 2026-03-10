import os

class DevelopmentConfig:
   SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-only-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///dev_blog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    FLASK_ENV = 'development'