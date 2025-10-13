from models import db
from datetime import datetime

class Demanda(db.Model):
    __tablename__ = 'demandas'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    setor_responsavel = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Nova', index=True)
    valor_estimado = db.Column(db.Float, default=0.0)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    data_conclusao = db.Column(db.DateTime)
    historico = db.Column(db.Text)
    arquivo_anexo = db.Column(db.String(255))
    convertida_projeto = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Demanda {self.id} - {self.tipo}>'
