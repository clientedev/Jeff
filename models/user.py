from models import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default='Leitor')
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acesso = db.Column(db.DateTime)
    
    telefone = db.Column(db.String(20))
    especialidade = db.Column(db.String(100))
    bio = db.Column(db.Text)
    foto_url = db.Column(db.String(500))
    
    visitas = db.relationship('Visita', backref='responsavel_user', lazy=True)
    demandas = db.relationship('Demanda', backref='responsavel_user', lazy=True)
    
    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)
    
    def is_admin(self):
        return self.perfil == 'Administrador'
    
    def is_coordenador(self):
        return self.perfil in ['Administrador', 'Coordenador']
    
    def is_atendente(self):
        return self.perfil in ['Administrador', 'Coordenador', 'Atendente']
    
    def is_consultor(self):
        return self.perfil in ['Administrador', 'Coordenador', 'Consultor']
    
    def __repr__(self):
        return f'<User {self.email}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
