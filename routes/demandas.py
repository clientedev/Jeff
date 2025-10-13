from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes import demandas_bp
from models import db
from models.demanda import Demanda
from models.empresa import Empresa
from models.log import Log
from datetime import datetime

@demandas_bp.route('/demandas')
@login_required
def lista():
    page = request.args.get('page', 1, type=int)
    demandas = Demanda.query.order_by(Demanda.data_criacao.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('demandas/lista.html', demandas=demandas)

@demandas_bp.route('/demandas/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if not current_user.is_atendente():
        flash('Você não tem permissão para criar demandas.', 'danger')
        return redirect(url_for('demandas.lista'))
    
    if request.method == 'POST':
        demanda = Demanda(
            empresa_id=request.form.get('empresa_id'),
            tipo=request.form.get('tipo'),
            descricao=request.form.get('descricao'),
            setor_responsavel=request.form.get('setor_responsavel'),
            status=request.form.get('status', 'Nova'),
            valor_estimado=float(request.form.get('valor_estimado', 0)),
            responsavel_id=current_user.id
        )
        
        db.session.add(demanda)
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='CRIAR_DEMANDA',
            descricao=f'Criou demanda tipo {demanda.tipo} para empresa ID {demanda.empresa_id}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Demanda cadastrada com sucesso!', 'success')
        return redirect(url_for('demandas.lista'))
    
    empresas = Empresa.query.order_by(Empresa.nome).all()
    return render_template('demandas/form.html', demanda=None, empresas=empresas)

@demandas_bp.route('/demandas/<int:id>')
@login_required
def detalhes(id):
    demanda = Demanda.query.get_or_404(id)
    return render_template('demandas/detalhes.html', demanda=demanda)

@demandas_bp.route('/demandas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not current_user.is_atendente():
        flash('Você não tem permissão para editar demandas.', 'danger')
        return redirect(url_for('demandas.lista'))
    
    demanda = Demanda.query.get_or_404(id)
    
    if request.method == 'POST':
        demanda.empresa_id = request.form.get('empresa_id')
        demanda.tipo = request.form.get('tipo')
        demanda.descricao = request.form.get('descricao')
        demanda.setor_responsavel = request.form.get('setor_responsavel')
        demanda.status = request.form.get('status')
        demanda.valor_estimado = float(request.form.get('valor_estimado', 0))
        demanda.convertida_projeto = request.form.get('convertida_projeto') == 'on'
        
        if demanda.status == 'Concluída' and not demanda.data_conclusao:
            demanda.data_conclusao = datetime.utcnow()
        
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='EDITAR_DEMANDA',
            descricao=f'Editou demanda ID {demanda.id}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Demanda atualizada com sucesso!', 'success')
        return redirect(url_for('demandas.detalhes', id=demanda.id))
    
    empresas = Empresa.query.order_by(Empresa.nome).all()
    return render_template('demandas/form.html', demanda=demanda, empresas=empresas)

@demandas_bp.route('/demandas/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    if not current_user.is_coordenador():
        flash('Você não tem permissão para excluir demandas.', 'danger')
        return redirect(url_for('demandas.lista'))
    
    demanda = Demanda.query.get_or_404(id)
    
    log = Log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao='EXCLUIR_DEMANDA',
        descricao=f'Excluiu demanda ID {id}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.delete(demanda)
    db.session.commit()
    
    flash('Demanda excluída com sucesso!', 'success')
    return redirect(url_for('demandas.lista'))
