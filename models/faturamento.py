from models import db
from datetime import datetime

class Faturamento(db.Model):
    __tablename__ = 'faturamento'
    
    id = db.Column(db.Integer, primary_key=True)
    proposta_id = db.Column(db.Integer, db.ForeignKey('propostas.id'), nullable=True)
    descricao = db.Column(db.String(300))
    valor = db.Column(db.Float, nullable=False)
    data_prevista = db.Column(db.Date)
    data_realizada = db.Column(db.Date)
    status = db.Column(db.String(50), default='Pendente')
    tipo = db.Column(db.String(100))
    nota_fiscal = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Faturamento {self.descricao} - R$ {self.valor}>'
