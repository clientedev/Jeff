from models import db
from datetime import datetime

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    usuario_email = db.Column(db.String(120))
    acao = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    data_hora = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    usuario = db.relationship('User', backref='logs')
    
    def __repr__(self):
        return f'<Log {self.acao} by {self.usuario_email}>'
