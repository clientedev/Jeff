from models import db
from datetime import datetime

class Visita(db.Model):
    __tablename__ = 'visitas'
    
    id = db.Column(db.Integer, primary_key=True)
    data_visita = db.Column(db.Date, nullable=False, index=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresas.id'), nullable=False)
    responsavel_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    objetivo = db.Column(db.String(200))
    resumo = db.Column(db.Text)
    proximos_passos = db.Column(db.Text)
    status = db.Column(db.String(50), default='Planejada')
    localizacao = db.Column(db.String(300))
    arquivo_relatorio = db.Column(db.String(255))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Visita {self.id} - {self.empresa.nome if self.empresa else "N/A"}>'
