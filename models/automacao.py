from models import db
from datetime import datetime

class Automacao(db.Model):
    __tablename__ = 'automacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    gatilho = db.Column(db.String(50), nullable=False)
    destinatarios = db.Column(db.Text)
    assunto = db.Column(db.String(200))
    mensagem = db.Column(db.Text, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_execucao = db.Column(db.DateTime)
    total_envios = db.Column(db.Integer, default=0)
    
    criado_por = db.relationship('User', backref='automacoes_criadas')
    logs = db.relationship('LogAutomacao', backref='automacao', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Automacao {self.nome}>'

class LogAutomacao(db.Model):
    __tablename__ = 'logs_automacao'
    
    id = db.Column(db.Integer, primary_key=True)
    automacao_id = db.Column(db.Integer, db.ForeignKey('automacoes.id'), nullable=False)
    destinatario = db.Column(db.String(200))
    status = db.Column(db.String(20))
    mensagem_erro = db.Column(db.Text)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LogAutomacao {self.id}>'
