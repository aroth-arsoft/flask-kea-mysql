import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://kea:kea@localhost:5306/kea"

SECRET_KEY="powerful secretkey"
WTF_CSRF_SECRET_KEY="a csrf secret key"
