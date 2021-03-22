from config import SQLALCHEMY_DATABASE_URI
from eralchemy import render_er

render_er(SQLALCHEMY_DATABASE_URI, 'app/static/erd.png')
