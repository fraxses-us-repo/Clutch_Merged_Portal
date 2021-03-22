import os
from flask_appbuilder.security.manager import (
    AUTH_OID,
    AUTH_REMOTE_USER,
    AUTH_DB,
    AUTH_LDAP,
    AUTH_OAUTH,
)

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "\2\1thisismyscretkey\1\2\e\y\y\h"

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://fraxses:fraxses@db:5432/clutch_diagnostics'
#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://fraxses:Fr@xses2020@cloudsql-proxy:5432/clutch_v2'
#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://clutch:Intenda#01@fraxses-pgr-svc-headless:5432/clutch_diagnostics'
#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{database_user}:{database_password}@{database_host}:{database_port}/{database_db}?options=-csearch_path%3Dclutch'.format(database_user='clutch', database_password='Intenda#01', database_host='clutch-pgr-svc-headless', database_port='5432', database_db='clutch_diagnostics')
#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{database_user}:{database_password}@{database_host}:{database_port}/{database_db}'.format(database_user='clutch', database_password='Intenda#01', database_host='clutch-pgr-svc-headless', database_port='5432', database_db='clutch_diagnostics')

AUTH_ROLE_ADMIN = "Admin"
AUTH_ROLE_PUBLIC = "Public"
# --------------------------------------
# User registration
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Employee"
# Config for Flask-WTF Recaptcha necessary for user registration
RECAPTCHA_PUBLIC_KEY = "6Le0ITwaAAAAAPnokmL-8KnI21Z_VQGWm38metH9"
RECAPTCHA_PRIVATE_KEY = "6Le0ITwaAAAAAHauabUI37VDXGyzRnuAAB3wJaVw"
# Config for Flask-Mail necessary for user registration
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_SERVER = "smtp.gmail.com"
MAIL_USE_TLS = True
MAIL_USERNAME = "app@clutch.health"
MAIL_PASSWORD = "hsjpvvjxadqfmyhh"
MAIL_DEFAULT_SENDER = "app@clutch.health"
# --------------------------------------
SQLALCHEMY_TRACK_MODIFICATIONS = False

WTF_CSRF_ENABLED = True

APP_NAME = "Clutch Diagnostics"

APP_ICON = "https://storage.googleapis.com/superset-static/clutch_logo.png"

FAB_API_SWAGGER_UI = True
AUTH_TYPE = 1

UPLOAD_FOLDER = basedir + "/app/static/uploads/"

# The image upload folder, when using models with images
IMG_UPLOAD_FOLDER = basedir + "/app/static/uploads/"

# The image upload url, when using models with images
IMG_UPLOAD_URL = "/static/uploads/"
# Setup image size default is (300, 200, True)
# IMG_SIZE = (300, 200, True)

