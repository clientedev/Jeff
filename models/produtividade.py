from models import db
from datetime import datetime

class Produtividade(db.Model):
    __tablename__ = 'produtividade'
    
    id = db.Column(db.Integer, primary_key=True)
    consultor = db.Column(db.String(200), nullable=False, index=True)
    mes = db.Column(db.Integer)
    ano = db.Column(db.Integer)
    horas_trabalhadas = db.Column(db.Float)
    horas_planejadas = db.Column(db.Float)
    numero_propostas = db.Column(db.Integer, default=0)
    numero_visitas = db.Column(db.Integer, default=0)
    numero_relatorios = db.Column(db.Integer, default=0)
    percentual_produtividade = db.Column(db.Float)
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Produtividade {self.consultor} - {self.mes}/{self.ano}>'
