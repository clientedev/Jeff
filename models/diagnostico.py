from models import db
from datetime import datetime

class Diagnostico(db.Model):
    __tablename__ = 'diagnosticos'
    
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    consultor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    visita_id = db.Column(db.Integer, db.ForeignKey('visitas.id'))
    tipo = db.Column(db.String(50), nullable=False)
    data_diagnostico = db.Column(db.Date, nullable=False)
    
    situacao_atual = db.Column(db.Text)
    problemas_identificados = db.Column(db.Text)
    oportunidades = db.Column(db.Text)
    recomendacoes = db.Column(db.Text)
    prioridade = db.Column(db.String(20), default='Média')
    
    score_producao = db.Column(db.Integer)
    score_qualidade = db.Column(db.Integer)
    score_logistica = db.Column(db.Integer)
    score_gestao = db.Column(db.Integer)
    score_manutencao = db.Column(db.Integer)
    score_geral = db.Column(db.Integer)
    
    investimento_estimado = db.Column(db.Float)
    retorno_estimado = db.Column(db.Float)
    prazo_implementacao = db.Column(db.String(50))
    
    status = db.Column(db.String(30), default='Pendente')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    consultor = db.relationship('User', backref='diagnosticos_realizados')
    empresa = db.relationship('Empresa', backref='diagnosticos')
    visita = db.relationship('Visita', backref='diagnosticos')
    melhorias = db.relationship('Melhoria', backref='diagnostico', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Diagnostico {self.id} - {self.tipo}>'

class Melhoria(db.Model):
    __tablename__ = 'melhorias'
    
    id = db.Column(db.Integer, primary_key=True)
    diagnostico_id = db.Column(db.Integer, db.ForeignKey('diagnosticos.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    area_afetada = db.Column(db.String(100))
    prioridade = db.Column(db.String(20), default='Média')
    custo_estimado = db.Column(db.Float)
    beneficio_estimado = db.Column(db.Float)
    prazo = db.Column(db.String(50))
    status = db.Column(db.String(30), default='Proposta')
    responsavel = db.Column(db.String(100))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.Date)
    
    def __repr__(self):
        return f'<Melhoria {self.titulo}>'
