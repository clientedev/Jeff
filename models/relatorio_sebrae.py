from models import db
from datetime import datetime

class RelatorioSebrae(db.Model):
    __tablename__ = 'relatorios_sebrae'
    
    id = db.Column(db.Integer, primary_key=True)
    proposta_numero = db.Column(db.String(50), index=True)
    empresa = db.Column(db.String(200))
    tipo_relatorio = db.Column(db.String(100))
    data_entrega = db.Column(db.Date)
    status = db.Column(db.String(50))
    responsavel = db.Column(db.String(200))
    arquivo_url = db.Column(db.String(500))
    observacoes = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<RelatorioSebrae {self.proposta_numero} - {self.tipo_relatorio}>'
