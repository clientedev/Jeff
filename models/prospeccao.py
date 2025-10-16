from models import db
from datetime import datetime

class Prospeccao(db.Model):
    __tablename__ = 'prospeccao'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(20), index=True)
    contato = db.Column(db.String(200))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(200))
    porte = db.Column(db.String(50))
    segmento = db.Column(db.String(100))
    origem = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Em prospecção')
    responsavel = db.Column(db.String(200))
    data_contato = db.Column(db.Date)
    data_retorno = db.Column(db.Date)
    interesse = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prospeccao {self.empresa}>'
