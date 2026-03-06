import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'prod_secret_key_abcdef'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///prod_blog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    FLASK_ENV = 'production'