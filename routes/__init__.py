from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
empresas_bp = Blueprint('empresas', __name__)
visitas_bp = Blueprint('visitas', __name__)
demandas_bp = Blueprint('demandas', __name__)
relatorios_bp = Blueprint('relatorios', __name__)
admin_bp = Blueprint('admin', __name__)

from routes import auth, dashboard, empresas, visitas, demandas, relatorios, admin
