from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.diagnostico import Diagnostico, Melhoria
from models.empresa import Empresa
from models.user import User
from sqlalchemy import func
from datetime import datetime

diagnosticos_bp = Blueprint('diagnosticos', __name__, url_prefix='/diagnosticos')

AREAS_DIAGNOSTICO = [
    'Producao',
    'Qualidade',
    'Manutencao',
    'Logistica',
    'Gestao',
    'Comercial',
    'Financeiro',
    'Recursos Humanos',
    'Seguranca do Trabalho',
    'Meio Ambiente'
]

@diagnosticos_bp.route('/')
@login_required
def index():
    if current_user.is_consultor() and not current_user.is_atendente():
        diagnosticos = Diagnostico.query.filter_by(consultor_id=current_user.id).all()
    else:
        diagnosticos = Diagnostico.query.all()
    
    total_diagnosticos = len(diagnosticos)
    total_melhorias = Melhoria.query.join(Diagnostico).filter(
        Diagnostico.id.in_([d.id for d in diagnosticos])
    ).count()
    melhorias_implementadas = Melhoria.query.join(Diagnostico).filter(
        Diagnostico.id.in_([d.id for d in diagnosticos]),
        Melhoria.status == 'Implementada'
    ).count()
    
    empresas_diagnosticadas = len(set([d.empresa_id for d in diagnosticos]))
    
    por_area = db.session.query(
        Diagnostico.area,
        func.count(Diagnostico.id)
    ).filter(Diagnostico.id.in_([d.id for d in diagnosticos])).group_by(Diagnostico.area).all()
    
    return render_template('diagnosticos/index.html',
                         diagnosticos=diagnosticos,
                         total_diagnosticos=total_diagnosticos,
                         total_melhorias=total_melhorias,
                         melhorias_implementadas=melhorias_implementadas,
                         empresas_diagnosticadas=empresas_diagnosticadas,
                         por_area=por_area)

@diagnosticos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if not current_user.is_consultor():
        flash('Apenas consultores podem criar diagnosticos.', 'danger')
        return redirect(url_for('diagnosticos.index'))
    
    if request.method == 'POST':
        diagnostico = Diagnostico(
            empresa_id=request.form['empresa_id'],
            consultor_id=current_user.id,
            area=request.form['area'],
            data_diagnostico=datetime.strptime(request.form['data_diagnostico'], '%Y-%m-%d').date(),
            situacao_atual=request.form.get('situacao_atual'),
            pontos_fortes=request.form.get('pontos_fortes'),
            oportunidades_melhoria=request.form.get('oportunidades_melhoria'),
            riscos_identificados=request.form.get('riscos_identificados'),
            recomendacoes=request.form.get('recomendacoes'),
            nota_geral=int(request.form.get('nota_geral', 0))
        )
        db.session.add(diagnostico)
        db.session.flush()
        
        melhorias_desc = request.form.getlist('melhoria_descricao[]')
        melhorias_prio = request.form.getlist('melhoria_prioridade[]')
        melhorias_prazo = request.form.getlist('melhoria_prazo[]')
        
        for desc, prio, prazo in zip(melhorias_desc, melhorias_prio, melhorias_prazo):
            if desc.strip():
                melhoria = Melhoria(
                    diagnostico_id=diagnostico.id,
                    descricao=desc,
                    prioridade=prio,
                    prazo_estimado=prazo,
                    status='Pendente'
                )
                db.session.add(melhoria)
        
        db.session.commit()
        flash('Diagnostico criado com sucesso!', 'success')
        return redirect(url_for('diagnosticos.detalhes', id=diagnostico.id))
    
    empresas = Empresa.query.filter_by(status='Ativo').all()
    return render_template('diagnosticos/form.html', 
                         empresas=empresas,
                         areas=AREAS_DIAGNOSTICO)

@diagnosticos_bp.route('/<int:id>')
@login_required
def detalhes(id):
    diagnostico = Diagnostico.query.get_or_404(id)
    
    if current_user.is_consultor() and not current_user.is_atendente():
        if diagnostico.consultor_id != current_user.id:
            flash('Acesso negado.', 'danger')
            return redirect(url_for('diagnosticos.index'))
    
    melhorias = Melhoria.query.filter_by(diagnostico_id=id).all()
    
    return render_template('diagnosticos/detalhes.html',
                         diagnostico=diagnostico,
                         melhorias=melhorias)

@diagnosticos_bp.route('/melhoria/<int:id>/atualizar', methods=['POST'])
@login_required
def atualizar_melhoria(id):
    melhoria = Melhoria.query.get_or_404(id)
    diagnostico = melhoria.diagnostico
    
    if not (current_user.is_atendente() or current_user.id == diagnostico.consultor_id):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('diagnosticos.index'))
    
    melhoria.status = request.form.get('status', melhoria.status)
    melhoria.data_implementacao = datetime.strptime(request.form['data_implementacao'], '%Y-%m-%d').date() if request.form.get('data_implementacao') else None
    melhoria.resultado = request.form.get('resultado', melhoria.resultado)
    
    db.session.commit()
    flash('Melhoria atualizada com sucesso!', 'success')
    return redirect(url_for('diagnosticos.detalhes', id=diagnostico.id))
