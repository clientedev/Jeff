from models import db
from datetime import datetime

class Proposta(db.Model):
    __tablename__ = 'propostas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_proposta = db.Column(db.String(50), unique=True, nullable=False, index=True)
    empresa_nome = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(20), index=True)
    sigla = db.Column(db.String(50))
    er = db.Column(db.String(100))
    porte = db.Column(db.String(50))
    solucao = db.Column(db.Text)
    horas = db.Column(db.Integer)
    consultor_principal = db.Column(db.String(200))
    data_inicio = db.Column(db.Date)
    data_termino = db.Column(db.Date)
    endereco = db.Column(db.String(300))
    regiao = db.Column(db.String(100))
    municipio = db.Column(db.String(100))
    uf = db.Column(db.String(20))
    contato = db.Column(db.String(200))
    telefone = db.Column(db.String(50))
    celular = db.Column(db.String(50))
    status = db.Column(db.String(50), default='Em andamento')
    tipo_programa = db.Column(db.String(100))
    etapa = db.Column(db.String(100))
    valor = db.Column(db.Float)
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    cronogramas = db.relationship('CronogramaAtividade', backref='proposta', lazy=True, cascade='all, delete-orphan')
    faturamentos = db.relationship('Faturamento', backref='proposta', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Proposta {self.numero_proposta} - {self.empresa_nome}>'
