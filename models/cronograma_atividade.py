from models import db
from datetime import datetime

class CronogramaAtividade(db.Model):
    __tablename__ = 'cronograma_atividades'
    
    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(db.Integer, db.ForeignKey('propostas.id'), nullable=False)
    atividade = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    data_prevista = db.Column(db.Date)
    data_realizada = db.Column(db.Date)
    status = db.Column(db.String(50), default='Pendente')
    responsavel = db.Column(db.String(200))
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CronogramaAtividade {self.atividade}>'
