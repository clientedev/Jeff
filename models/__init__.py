from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

from models.user import User
from models.empresa import Empresa
from models.visita import Visita
from models.demanda import Demanda
from models.log import Log
from models.inovacao import Inovacao, InovacaoEmpresa
from models.formulario import Formulario, RespostaFormulario
from models.diagnostico import Diagnostico, Melhoria
from models.automacao import Automacao, LogAutomacao
from models.proposta import Proposta
from models.cronograma_atividade import CronogramaAtividade
from models.produtividade import Produtividade
from models.faturamento import Faturamento
from models.controle_sgt import ControleSGT
from models.relatorio_sebrae import RelatorioSebrae
from models.prospeccao import Prospeccao
from models.followup import FollowUp
