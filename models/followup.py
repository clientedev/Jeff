from models import db
from datetime import datetime

class FollowUp(db.Model):
    __tablename__ = 'followup'
    
    id = db.Column(db.Integer, primary_key=True)
    proposta_numero = db.Column(db.String(50), index=True)
    empresa = db.Column(db.String(200))
    tipo = db.Column(db.String(100))
    data_acao = db.Column(db.Date)
    responsavel = db.Column(db.String(200))
    status = db.Column(db.String(50))
    descricao = db.Column(db.Text)
    resultado = db.Column(db.Text)
    proxima_acao = db.Column(db.Text)
    data_proxima_acao = db.Column(db.Date)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FollowUp {self.proposta_numero} - {self.tipo}>'
