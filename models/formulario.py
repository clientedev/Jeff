from models import db
from datetime import datetime
import secrets

class Formulario(db.Model):
    __tablename__ = 'formularios'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    token = db.Column(db.String(64), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'))
    criado_por_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    expira_em = db.Column(db.DateTime)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    criado_por = db.relationship('User', backref='formularios_criados')
    empresa = db.relationship('Empresa', backref='formularios')
    respostas = db.relationship('RespostaFormulario', backref='formulario', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Formulario {self.titulo}>'

class RespostaFormulario(db.Model):
    __tablename__ = 'respostas_formularios'
    
    id = db.Column(db.Integer, primary_key=True)
    formulario_id = db.Column(db.Integer, db.ForeignKey('formularios.id'), nullable=False)
    dados_json = db.Column(db.JSON, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    data_resposta = db.Column(db.DateTime, default=datetime.utcnow)
    processado = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<RespostaFormulario {self.id}>'
