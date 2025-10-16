from models import db
from datetime import datetime

class ControleSGT(db.Model):
    __tablename__ = 'controle_sgt'
    
    id = db.Column(db.Integer, primary_key=True)
    proposta_numero = db.Column(db.String(50), index=True)
    empresa = db.Column(db.String(200))
    etapa = db.Column(db.String(100))
    status = db.Column(db.String(100))
    data_inicio = db.Column(db.Date)
    data_prevista = db.Column(db.Date)
    data_conclusao = db.Column(db.Date)
    responsavel = db.Column(db.String(200))
    percentual_conclusao = db.Column(db.Float, default=0)
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ControleSGT {self.proposta_numero} - {self.etapa}>'
