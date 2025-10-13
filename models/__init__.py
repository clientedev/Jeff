from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

from models.user import User
from models.empresa import Empresa
from models.visita import Visita
from models.demanda import Demanda
from models.log import Log
