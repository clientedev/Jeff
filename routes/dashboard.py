from flask import render_template
from flask_login import login_required, current_user
from routes import dashboard_bp
from models import db
from models.empresa import Empresa
from models.visita import Visita
from models.demanda import Demanda
from sqlalchemy import func, extract
from datetime import datetime, timedelta

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    total_empresas = Empresa.query.count()
    empresas_ativas = Empresa.query.filter_by(status='Ativo').count()
    
    total_visitas = Visita.query.count()
    visitas_mes = Visita.query.filter(
        extract('month', Visita.data_visita) == datetime.now().month,
        extract('year', Visita.data_visita) == datetime.now().year
    ).count()
    
    total_demandas = Demanda.query.count()
    demandas_abertas = Demanda.query.filter(Demanda.status.in_(['Nova', 'Em andamento'])).count()
    demandas_concluidas = Demanda.query.filter_by(status='Concluída').count()
    
    valor_total_oportunidades = db.session.query(func.sum(Demanda.valor_estimado)).scalar() or 0
    
    demandas_convertidas = Demanda.query.filter_by(convertida_projeto=True).count()
    taxa_conversao = (demandas_convertidas / total_demandas * 100) if total_demandas > 0 else 0
    
    visitas_por_status = db.session.query(
        Visita.status, func.count(Visita.id)
    ).group_by(Visita.status).all()
    
    demandas_por_status = db.session.query(
        Demanda.status, func.count(Demanda.id)
    ).group_by(Demanda.status).all()
    
    empresas_por_segmento = db.session.query(
        Empresa.segmento, func.count(Empresa.id)
    ).group_by(Empresa.segmento).limit(10).all()
    
    ultimas_visitas = Visita.query.order_by(Visita.data_criacao.desc()).limit(5).all()
    ultimas_demandas = Demanda.query.order_by(Demanda.data_criacao.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_empresas=total_empresas,
                         empresas_ativas=empresas_ativas,
                         total_visitas=total_visitas,
                         visitas_mes=visitas_mes,
                         total_demandas=total_demandas,
                         demandas_abertas=demandas_abertas,
                         demandas_concluidas=demandas_concluidas,
                         valor_total_oportunidades=valor_total_oportunidades,
                         taxa_conversao=taxa_conversao,
                         visitas_por_status=visitas_por_status,
                         demandas_por_status=demandas_por_status,
                         empresas_por_segmento=empresas_por_segmento,
                         ultimas_visitas=ultimas_visitas,
                         ultimas_demandas=ultimas_demandas)
