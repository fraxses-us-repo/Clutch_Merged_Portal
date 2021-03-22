import logging
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.menu import Menu
from app.security import CustomSecurityManager
from app.index import MyIndexView
#from flask_bootstrap import Bootstrap

try:
    from flask_mail import Mail
    mail = Mail(app)
except:
    pass

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_object("config")
db = SQLA(app)
appbuilder = AppBuilder(app, db.session, indexview=MyIndexView, menu=Menu(reverse=False), security_manager_class=CustomSecurityManager, base_template='custom_base.html')

from . import views
