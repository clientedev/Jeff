from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from models import db
from models.empresa import Empresa
from models.user import User
from models.visita import Visita
from models.demanda import Demanda
from models.inovacao import InovacaoEmpresa
from models.diagnostico import Diagnostico
from routes import carteira_bp
from sqlalchemy import func, or_, and_
from datetime import datetime, timedelta
import json

@carteira_bp.route('/')
@login_required
def index():
    consultor_id = request.args.get('consultor_id', type=int)
    segmento = request.args.get('segmento', '')
    porte = request.args.get('porte', '')
    status = request.args.get('status', '')
    cidade = request.args.get('cidade', '')
    
    query = Empresa.query
    
    if current_user.perfil == 'Consultor':
        consultor_id = current_user.id
    
    if consultor_id:
        query = query.join(Visita).filter(Visita.responsavel_id == consultor_id)
    
    if segmento:
        query = query.filter(Empresa.segmento.ilike(f'%{segmento}%'))
    if porte:
        query = query.filter(Empresa.porte == porte)
    if status:
        query = query.filter(Empresa.status == status)
    if cidade:
        query = query.filter(Empresa.cidade.ilike(f'%{cidade}%'))
    
    empresas_query = query.distinct().order_by(Empresa.nome)
    
    empresas_com_stats = []
    for empresa in empresas_query.all():
        total_visitas = Visita.query.filter_by(empresa_id=empresa.id).count()
        total_demandas = Demanda.query.filter_by(empresa_id=empresa.id).count()
        total_inovacoes = InovacaoEmpresa.query.filter_by(empresa_id=empresa.id).count()
        total_diagnosticos = Diagnostico.query.filter_by(empresa_id=empresa.id).count()
        
        ultima_visita = Visita.query.filter_by(empresa_id=empresa.id).order_by(Visita.data_visita.desc()).first()
        
        demandas_abertas = Demanda.query.filter_by(empresa_id=empresa.id).filter(
            Demanda.status.in_(['Nova', 'Em andamento'])
        ).count()
        
        inovacoes_ativas = InovacaoEmpresa.query.filter_by(empresa_id=empresa.id).filter(
            InovacaoEmpresa.status.in_(['Planejada', 'Em Implementação'])
        ).count()
        
        nivel_engajamento = 'Baixo'
        if total_visitas >= 5 or total_demandas >= 3:
            nivel_engajamento = 'Alto'
        elif total_visitas >= 2 or total_demandas >= 1:
            nivel_engajamento = 'Médio'
        
        empresas_com_stats.append({
            'empresa': empresa,
            'total_visitas': total_visitas,
            'total_demandas': total_demandas,
            'total_inovacoes': total_inovacoes,
            'total_diagnosticos': total_diagnosticos,
            'ultima_visita': ultima_visita,
            'demandas_abertas': demandas_abertas,
            'inovacoes_ativas': inovacoes_ativas,
            'nivel_engajamento': nivel_engajamento
        })
    
    consultores = User.query.filter(
        or_(User.perfil == 'Consultor', User.perfil == 'Coordenador', User.perfil == 'Administrador')
    ).filter_by(ativo=True).order_by(User.nome).all()
    
    segmentos = db.session.query(Empresa.segmento).distinct().order_by(Empresa.segmento).all()
    portes = db.session.query(Empresa.porte).distinct().order_by(Empresa.porte).all()
    cidades = db.session.query(Empresa.cidade).distinct().order_by(Empresa.cidade).all()
    
    return render_template('carteira/index.html',
                         empresas=empresas_com_stats,
                         consultores=consultores,
                         segmentos=[s[0] for s in segmentos if s[0]],
                         portes=[p[0] for p in portes if p[0]],
                         cidades=[c[0] for c in cidades if c[0]],
                         consultor_id=consultor_id,
                         filtro_segmento=segmento,
                         filtro_porte=porte,
                         filtro_status=status,
                         filtro_cidade=cidade)

@carteira_bp.route('/empresa/<int:empresa_id>')
@login_required
def detalhes_empresa(empresa_id):
    empresa = Empresa.query.get_or_404(empresa_id)
    
    visitas = Visita.query.filter_by(empresa_id=empresa_id).order_by(Visita.data_visita.desc()).all()
    demandas = Demanda.query.filter_by(empresa_id=empresa_id).order_by(Demanda.data_criacao.desc()).all()
    inovacoes = InovacaoEmpresa.query.filter_by(empresa_id=empresa_id).order_by(InovacaoEmpresa.data_atribuicao.desc()).all()
    diagnosticos = Diagnostico.query.filter_by(empresa_id=empresa_id).order_by(Diagnostico.data_diagnostico.desc()).all()
    
    demandas_por_status = db.session.query(
        Demanda.status, func.count(Demanda.id)
    ).filter_by(empresa_id=empresa_id).group_by(Demanda.status).all()
    
    inovacoes_por_status = db.session.query(
        InovacaoEmpresa.status, func.count(InovacaoEmpresa.id)
    ).filter_by(empresa_id=empresa_id).group_by(InovacaoEmpresa.status).all()
    
    timeline = []
    
    for visita in visitas:
        timeline.append({
            'tipo': 'visita',
            'data': visita.data_visita,
            'titulo': f'Visita Técnica - {visita.objetivo or "Sem objetivo"}',
            'descricao': visita.resumo,
            'status': visita.status,
            'responsavel': visita.responsavel_user.nome if visita.responsavel_user else 'N/A'
        })
    
    for demanda in demandas:
        timeline.append({
            'tipo': 'demanda',
            'data': demanda.data_criacao.date(),
            'titulo': f'Demanda - {demanda.tipo}',
            'descricao': demanda.descricao[:150] + '...' if len(demanda.descricao) > 150 else demanda.descricao,
            'status': demanda.status,
            'responsavel': demanda.responsavel_user.nome if demanda.responsavel_user else 'N/A'
        })
    
    for inovacao in inovacoes:
        timeline.append({
            'tipo': 'inovacao',
            'data': inovacao.data_atribuicao.date(),
            'titulo': f'Inovação - {inovacao.inovacao.nome}',
            'descricao': f'Progresso: {inovacao.progresso}%',
            'status': inovacao.status,
            'responsavel': inovacao.consultor.nome if inovacao.consultor else 'N/A'
        })
    
    timeline.sort(key=lambda x: x['data'], reverse=True)
    
    return render_template('carteira/detalhes.html',
                         empresa=empresa,
                         visitas=visitas,
                         demandas=demandas,
                         inovacoes=inovacoes,
                         diagnosticos=diagnosticos,
                         demandas_por_status=demandas_por_status,
                         inovacoes_por_status=inovacoes_por_status,
                         timeline=timeline)

@carteira_bp.route('/stats')
@login_required
def stats():
    consultor_id = request.args.get('consultor_id', type=int)
    
    if current_user.perfil == 'Consultor':
        consultor_id = current_user.id
    
    empresas_ativas = Empresa.query.filter_by(status='Ativo').count()
    
    if consultor_id:
        total_visitas = Visita.query.filter_by(responsavel_id=consultor_id).count()
        empresas_atendidas = db.session.query(func.count(func.distinct(Visita.empresa_id))).filter_by(
            responsavel_id=consultor_id
        ).scalar()
    else:
        total_visitas = Visita.query.count()
        empresas_atendidas = db.session.query(func.count(func.distinct(Visita.empresa_id))).scalar()
    
    demandas_abertas = Demanda.query.filter(Demanda.status.in_(['Nova', 'Em andamento'])).count()
    inovacoes_ativas = InovacaoEmpresa.query.filter(InovacaoEmpresa.status.in_(['Planejada', 'Em Implementação'])).count()
    
    return jsonify({
        'empresas_ativas': empresas_ativas,
        'total_visitas': total_visitas,
        'empresas_atendidas': empresas_atendidas,
        'demandas_abertas': demandas_abertas,
        'inovacoes_ativas': inovacoes_ativas
    })
