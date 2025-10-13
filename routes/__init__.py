from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
dashboard_bp = Blueprint('dashboard', __name__)
empresas_bp = Blueprint('empresas', __name__)
visitas_bp = Blueprint('visitas', __name__)
demandas_bp = Blueprint('demandas', __name__)
relatorios_bp = Blueprint('relatorios', __name__)
admin_bp = Blueprint('admin', __name__)
carteira_bp = Blueprint('carteira', __name__, url_prefix='/carteira')
importacao_bp = Blueprint('importacao', __name__)
formularios_bp = Blueprint('formularios', __name__)
formulario_publico_bp = Blueprint('formulario_publico', __name__)

from routes.inovacoes import inovacoes_bp
from routes.consultores import consultores_bp
from routes.diagnosticos import diagnosticos_bp
from routes.automacoes import automacoes_bp

from routes import auth, dashboard, empresas, visitas, demandas, relatorios, admin, carteira, importacao, formularios, formulario_publico
