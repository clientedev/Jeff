from flask import render_template
from flask_login import login_required, current_user
from routes import dashboard_bp
from models import db
from models.empresa import Empresa
from models.visita import Visita
from models.demanda import Demanda
from models.inovacao import InovacaoEmpresa
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import json

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
    
    mes_anterior = datetime.now().month - 1 if datetime.now().month > 1 else 12
    ano_anterior = datetime.now().year if datetime.now().month > 1 else datetime.now().year - 1
    visitas_mes_anterior = Visita.query.filter(
        extract('month', Visita.data_visita) == mes_anterior,
        extract('year', Visita.data_visita) == ano_anterior
    ).count()
    
    total_demandas = Demanda.query.count()
    demandas_abertas = Demanda.query.filter(Demanda.status.in_(['Nova', 'Em andamento'])).count()
    demandas_concluidas = Demanda.query.filter_by(status='Concluída').count()
    
    valor_total_oportunidades = db.session.query(func.sum(Demanda.valor_estimado)).scalar() or 0
    
    demandas_convertidas = Demanda.query.filter_by(convertida_projeto=True).count()
    taxa_conversao = (demandas_convertidas / total_demandas * 100) if total_demandas > 0 else 0
    
    total_inovacoes = InovacaoEmpresa.query.count()
    inovacoes_concluidas = InovacaoEmpresa.query.filter_by(status='Concluída').count()
    
    visitas_por_status = db.session.query(
        Visita.status, func.count(Visita.id)
    ).group_by(Visita.status).all()
    
    demandas_por_status = db.session.query(
        Demanda.status, func.count(Demanda.id)
    ).group_by(Demanda.status).all()
    
    empresas_por_segmento = db.session.query(
        Empresa.segmento, func.count(Empresa.id)
    ).filter(Empresa.segmento.isnot(None)).group_by(Empresa.segmento).limit(8).all()
    
    empresas_por_porte = db.session.query(
        Empresa.porte, func.count(Empresa.id)
    ).filter(Empresa.porte.isnot(None)).group_by(Empresa.porte).all()
    
    visitas_ultimos_6_meses = []
    demandas_ultimas_6_meses = []
    labels_6_meses = []
    
    for i in range(5, -1, -1):
        data = datetime.now() - timedelta(days=i*30)
        mes = data.month
        ano = data.year
        
        labels_6_meses.append(data.strftime('%b/%y'))
        
        visitas_count = Visita.query.filter(
            extract('month', Visita.data_visita) == mes,
            extract('year', Visita.data_visita) == ano
        ).count()
        visitas_ultimos_6_meses.append(visitas_count)
        
        demandas_count = Demanda.query.filter(
            extract('month', Demanda.data_criacao) == mes,
            extract('year', Demanda.data_criacao) == ano
        ).count()
        demandas_ultimas_6_meses.append(demandas_count)
    
    demandas_por_tipo = db.session.query(
        Demanda.tipo, func.count(Demanda.id)
    ).filter(Demanda.tipo.isnot(None)).group_by(Demanda.tipo).all()
    
    ultimas_visitas = Visita.query.order_by(Visita.data_criacao.desc()).limit(5).all()
    ultimas_demandas = Demanda.query.order_by(Demanda.data_criacao.desc()).limit(5).all()
    
    crescimento_visitas = ((visitas_mes - visitas_mes_anterior) / visitas_mes_anterior * 100) if visitas_mes_anterior > 0 else 0
    
    return render_template('dashboard.html',
                         total_empresas=total_empresas,
                         empresas_ativas=empresas_ativas,
                         total_visitas=total_visitas,
                         visitas_mes=visitas_mes,
                         crescimento_visitas=crescimento_visitas,
                         total_demandas=total_demandas,
                         demandas_abertas=demandas_abertas,
                         demandas_concluidas=demandas_concluidas,
                         valor_total_oportunidades=valor_total_oportunidades,
                         taxa_conversao=taxa_conversao,
                         total_inovacoes=total_inovacoes,
                         inovacoes_concluidas=inovacoes_concluidas,
                         visitas_por_status=visitas_por_status,
                         demandas_por_status=demandas_por_status,
                         empresas_por_segmento=empresas_por_segmento,
                         empresas_por_porte=empresas_por_porte,
                         demandas_por_tipo=demandas_por_tipo,
                         visitas_ultimos_6_meses=json.dumps(visitas_ultimos_6_meses),
                         demandas_ultimas_6_meses=json.dumps(demandas_ultimas_6_meses),
                         labels_6_meses=json.dumps(labels_6_meses),
                         ultimas_visitas=ultimas_visitas,
                         ultimas_demandas=ultimas_demandas)
