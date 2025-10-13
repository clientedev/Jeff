from models import db
from datetime import datetime

class Inovacao(db.Model):
    __tablename__ = 'inovacoes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text)
    beneficios = db.Column(db.Text)
    requisitos = db.Column(db.Text)
    tempo_implementacao = db.Column(db.String(50))
    nivel_complexidade = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    atribuicoes = db.relationship('InovacaoEmpresa', backref='inovacao', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Inovacao {self.nome}>'

class InovacaoEmpresa(db.Model):
    __tablename__ = 'inovacoes_empresas'
    
    id = db.Column(db.Integer, primary_key=True)
    inovacao_id = db.Column(db.Integer, db.ForeignKey('inovacoes.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    consultor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(30), default='Planejada')
    data_atribuicao = db.Column(db.DateTime, default=datetime.utcnow)
    data_inicio = db.Column(db.Date)
    data_conclusao = db.Column(db.Date)
    progresso = db.Column(db.Integer, default=0)
    observacoes = db.Column(db.Text)
    resultados = db.Column(db.Text)
    investimento = db.Column(db.Float, default=0)
    economia_gerada = db.Column(db.Float, default=0)
    
    consultor = db.relationship('User', backref='inovacoes_atribuidas')
    empresa = db.relationship('Empresa', backref='inovacoes_aplicadas')
    
    def __repr__(self):
        return f'<InovacaoEmpresa {self.id}>'
