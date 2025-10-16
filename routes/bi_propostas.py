from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from models import db
from models.proposta import Proposta
from models.produtividade import Produtividade
from models.faturamento import Faturamento
from models.controle_sgt import ControleSGT
from sqlalchemy import func, extract
from datetime import datetime, timedelta

bi_propostas_bp = Blueprint('bi_propostas', __name__, url_prefix='/bi-propostas')

@bi_propostas_bp.route('/')
@login_required
def index():
    total_propostas = Proposta.query.count()
    propostas_ativas = Proposta.query.filter(
        Proposta.status.in_(['Em andamento', 'Ativa', 'Planejada'])
    ).count()
    propostas_concluidas = Proposta.query.filter(
        Proposta.status.in_(['Concluída', 'Finalizada'])
    ).count()
    
    total_horas = db.session.query(func.sum(Proposta.horas)).scalar() or 0
    total_faturamento = db.session.query(func.sum(Faturamento.valor)).filter(
        Faturamento.status == 'Realizado'
    ).scalar() or 0
    faturamento_previsto = db.session.query(func.sum(Faturamento.valor)).filter(
        Faturamento.status.in_(['Pendente', 'Previsto'])
    ).scalar() or 0
    
    propostas_por_er = db.session.query(
        Proposta.er,
        func.count(Proposta.id).label('total')
    ).filter(Proposta.er.isnot(None)).group_by(Proposta.er).order_by(func.count(Proposta.id).desc()).limit(10).all()
    
    propostas_por_consultor = db.session.query(
        Proposta.consultor_principal,
        func.count(Proposta.id).label('total'),
        func.sum(Proposta.horas).label('total_horas')
    ).filter(Proposta.consultor_principal.isnot(None)).group_by(Proposta.consultor_principal).order_by(func.count(Proposta.id).desc()).limit(10).all()
    
    propostas_por_status = db.session.query(
        Proposta.status,
        func.count(Proposta.id).label('total')
    ).filter(Proposta.status.isnot(None)).group_by(Proposta.status).all()
    
    propostas_por_porte = db.session.query(
        Proposta.porte,
        func.count(Proposta.id).label('total')
    ).filter(Proposta.porte.isnot(None)).group_by(Proposta.porte).all()
    
    return render_template('bi_propostas/index.html',
        total_propostas=total_propostas,
        propostas_ativas=propostas_ativas,
        propostas_concluidas=propostas_concluidas,
        total_horas=total_horas,
        total_faturamento=total_faturamento,
        faturamento_previsto=faturamento_previsto,
        propostas_por_er=propostas_por_er,
        propostas_por_consultor=propostas_por_consultor,
        propostas_por_status=propostas_por_status,
        propostas_por_porte=propostas_por_porte
    )

@bi_propostas_bp.route('/produtividade')
@login_required
def produtividade():
    produtividades = db.session.query(
        Produtividade.consultor,
        func.sum(Produtividade.horas_trabalhadas).label('horas_trabalhadas'),
        func.sum(Produtividade.horas_planejadas).label('horas_planejadas'),
        func.avg(Produtividade.percentual_produtividade).label('produtividade_media')
    ).group_by(Produtividade.consultor).all()
    
    produtividade_mensal = db.session.query(
        Produtividade.mes,
        Produtividade.ano,
        func.avg(Produtividade.percentual_produtividade).label('produtividade_media'),
        func.sum(Produtividade.horas_trabalhadas).label('horas_trabalhadas')
    ).filter(
        Produtividade.mes.isnot(None),
        Produtividade.ano.isnot(None)
    ).group_by(Produtividade.mes, Produtividade.ano).order_by(Produtividade.ano, Produtividade.mes).all()
    
    return render_template('bi_propostas/produtividade.html',
        produtividades=produtividades,
        produtividade_mensal=produtividade_mensal
    )

@bi_propostas_bp.route('/faturamento')
@login_required
def faturamento():
    faturamento_total = db.session.query(func.sum(Faturamento.valor)).scalar() or 0
    faturamento_realizado = db.session.query(func.sum(Faturamento.valor)).filter(
        Faturamento.status.in_(['Realizado', 'Pago', 'Faturado'])
    ).scalar() or 0
    faturamento_pendente = db.session.query(func.sum(Faturamento.valor)).filter(
        Faturamento.status.in_(['Pendente', 'Previsto', 'A receber'])
    ).scalar() or 0
    
    faturamento_por_mes = db.session.query(
        extract('month', Faturamento.data_realizada).label('mes'),
        extract('year', Faturamento.data_realizada).label('ano'),
        func.sum(Faturamento.valor).label('total')
    ).filter(
        Faturamento.data_realizada.isnot(None),
        Faturamento.status.in_(['Realizado', 'Pago', 'Faturado'])
    ).group_by('mes', 'ano').order_by('ano', 'mes').all()
    
    faturamento_por_tipo = db.session.query(
        Faturamento.tipo,
        func.sum(Faturamento.valor).label('total'),
        func.count(Faturamento.id).label('quantidade')
    ).filter(Faturamento.tipo.isnot(None)).group_by(Faturamento.tipo).all()
    
    return render_template('bi_propostas/faturamento.html',
        faturamento_total=faturamento_total,
        faturamento_realizado=faturamento_realizado,
        faturamento_pendente=faturamento_pendente,
        faturamento_por_mes=faturamento_por_mes,
        faturamento_por_tipo=faturamento_por_tipo
    )

@bi_propostas_bp.route('/cronogramas')
@login_required
def cronogramas():
    hoje = datetime.now().date()
    proximo_mes = hoje + timedelta(days=30)
    
    propostas_proximas = Proposta.query.filter(
        Proposta.data_termino.between(hoje, proximo_mes)
    ).order_by(Proposta.data_termino).all()
    
    propostas_atrasadas = Proposta.query.filter(
        Proposta.data_termino < hoje,
        Proposta.status.notin_(['Concluída', 'Finalizada', 'Cancelada'])
    ).order_by(Proposta.data_termino).all()
    
    propostas_timeline = Proposta.query.filter(
        Proposta.data_inicio.isnot(None),
        Proposta.data_termino.isnot(None)
    ).order_by(Proposta.data_inicio).limit(50).all()
    
    return render_template('bi_propostas/cronogramas.html',
        propostas_proximas=propostas_proximas,
        propostas_atrasadas=propostas_atrasadas,
        propostas_timeline=propostas_timeline
    )

@bi_propostas_bp.route('/api/chart-data')
@login_required
def chart_data():
    chart_type = request.args.get('type', 'propostas_status')
    
    if chart_type == 'propostas_status':
        data = db.session.query(
            Proposta.status,
            func.count(Proposta.id).label('total')
        ).filter(Proposta.status.isnot(None)).group_by(Proposta.status).all()
        
        return jsonify({
            'labels': [item[0] for item in data],
            'values': [item[1] for item in data]
        })
    
    return jsonify({'error': 'Invalid chart type'})
