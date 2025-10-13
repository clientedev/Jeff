from models import db
from datetime import datetime

class Empresa(db.Model):
    __tablename__ = 'empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, index=True)
    cnpj = db.Column(db.String(18), unique=True, index=True)
    ie = db.Column(db.String(20))
    segmento = db.Column(db.String(100))
    porte = db.Column(db.String(50))
    endereco = db.Column(db.String(300))
    cidade = db.Column(db.String(100), index=True)
    uf = db.Column(db.String(2))
    contato_principal = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    status = db.Column(db.String(50), default='Ativo')
    observacoes = db.Column(db.Text)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    responsavel = db.Column(db.String(100))
    
    visitas = db.relationship('Visita', backref='empresa', lazy=True, cascade='all, delete-orphan')
    demandas = db.relationship('Demanda', backref='empresa', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Empresa {self.nome}>'
