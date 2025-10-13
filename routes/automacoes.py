from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.automacao import Automacao, LogAutomacao
from models.empresa import Empresa
from sqlalchemy import func
from datetime import datetime

automacoes_bp = Blueprint('automacoes', __name__, url_prefix='/automacoes')

TIPOS_AUTOMACAO = ['Email', 'SMS', 'WhatsApp']
GATILHOS = [
    'Nova Empresa Cadastrada',
    'Visita Agendada',
    'Visita Realizada',
    'Demanda Criada',
    'Demanda Concluída',
    'Diagnóstico Realizado',
    'Inovação Atribuída',
    'Inovação Concluída',
    'Formulário Respondido',
    'Manual'
]

@automacoes_bp.route('/')
@login_required
def index():
    if not current_user.is_atendente():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    automacoes = Automacao.query.all()
    automacoes_ativas = Automacao.query.filter_by(ativa=True).count()
    
    total_envios = LogAutomacao.query.count()
    envios_sucesso = LogAutomacao.query.filter_by(status='Sucesso').count()
    envios_erro = LogAutomacao.query.filter_by(status='Erro').count()
    
    taxa_sucesso = (envios_sucesso / total_envios * 100) if total_envios > 0 else 0
    
    por_tipo = db.session.query(
        Automacao.tipo,
        func.count(Automacao.id)
    ).group_by(Automacao.tipo).all()
    
    ultimos_logs = LogAutomacao.query.order_by(LogAutomacao.data_envio.desc()).limit(20).all()
    
    return render_template('automacoes/index.html',
                         automacoes=automacoes,
                         automacoes_ativas=automacoes_ativas,
                         total_envios=total_envios,
                         envios_sucesso=envios_sucesso,
                         envios_erro=envios_erro,
                         taxa_sucesso=taxa_sucesso,
                         por_tipo=por_tipo,
                         ultimos_logs=ultimos_logs)

@automacoes_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if not current_user.is_atendente():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('automacoes.index'))
    
    if request.method == 'POST':
        automacao = Automacao(
            nome=request.form['nome'],
            tipo=request.form['tipo'],
            gatilho=request.form['gatilho'],
            destinatario_campo=request.form.get('destinatario_campo'),
            assunto=request.form.get('assunto'),
            corpo_mensagem=request.form.get('corpo_mensagem'),
            ativa=request.form.get('ativa') == 'on'
        )
        db.session.add(automacao)
        db.session.commit()
        
        flash('Automação criada com sucesso!', 'success')
        return redirect(url_for('automacoes.index'))
    
    return render_template('automacoes/form.html',
                         tipos=TIPOS_AUTOMACAO,
                         gatilhos=GATILHOS)

@automacoes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not current_user.is_atendente():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('automacoes.index'))
    
    automacao = Automacao.query.get_or_404(id)
    
    if request.method == 'POST':
        automacao.nome = request.form['nome']
        automacao.tipo = request.form['tipo']
        automacao.gatilho = request.form['gatilho']
        automacao.destinatario_campo = request.form.get('destinatario_campo')
        automacao.assunto = request.form.get('assunto')
        automacao.corpo_mensagem = request.form.get('corpo_mensagem')
        automacao.ativa = request.form.get('ativa') == 'on'
        
        db.session.commit()
        flash('Automação atualizada com sucesso!', 'success')
        return redirect(url_for('automacoes.index'))
    
    return render_template('automacoes/form.html',
                         automacao=automacao,
                         tipos=TIPOS_AUTOMACAO,
                         gatilhos=GATILHOS)

@automacoes_bp.route('/<int:id>/testar', methods=['POST'])
@login_required
def testar(id):
    if not current_user.is_atendente():
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403
    
    automacao = Automacao.query.get_or_404(id)
    destinatario = request.form.get('destinatario')
    
    log = LogAutomacao(
        automacao_id=automacao.id,
        destinatario=destinatario,
        status='Teste',
        mensagem='Envio de teste realizado'
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'Teste de automação realizado. Em produção, enviaria {automacao.tipo} para {destinatario}', 'info')
    return redirect(url_for('automacoes.index'))

@automacoes_bp.route('/logs')
@login_required
def logs():
    if not current_user.is_atendente():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    logs = LogAutomacao.query.order_by(LogAutomacao.data_envio.desc()).limit(200).all()
    
    return render_template('automacoes/logs.html', logs=logs)
