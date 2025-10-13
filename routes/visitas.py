from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes import visitas_bp
from models import db
from models.visita import Visita
from models.empresa import Empresa
from models.log import Log
from datetime import datetime

@visitas_bp.route('/visitas')
@login_required
def lista():
    page = request.args.get('page', 1, type=int)
    visitas = Visita.query.order_by(Visita.data_visita.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('visitas/lista.html', visitas=visitas)

@visitas_bp.route('/visitas/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if not current_user.is_atendente():
        flash('Você não tem permissão para criar visitas.', 'danger')
        return redirect(url_for('visitas.lista'))
    
    if request.method == 'POST':
        visita = Visita(
            data_visita=datetime.strptime(request.form.get('data_visita'), '%Y-%m-%d').date(),
            empresa_id=request.form.get('empresa_id'),
            responsavel_id=current_user.id,
            objetivo=request.form.get('objetivo'),
            resumo=request.form.get('resumo'),
            proximos_passos=request.form.get('proximos_passos'),
            status=request.form.get('status', 'Planejada'),
            localizacao=request.form.get('localizacao')
        )
        
        db.session.add(visita)
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='CRIAR_VISITA',
            descricao=f'Criou visita para empresa ID {visita.empresa_id}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Visita cadastrada com sucesso!', 'success')
        return redirect(url_for('visitas.lista'))
    
    empresas = Empresa.query.order_by(Empresa.nome).all()
    return render_template('visitas/form.html', visita=None, empresas=empresas)

@visitas_bp.route('/visitas/<int:id>')
@login_required
def detalhes(id):
    visita = Visita.query.get_or_404(id)
    return render_template('visitas/detalhes.html', visita=visita)

@visitas_bp.route('/visitas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not current_user.is_atendente():
        flash('Você não tem permissão para editar visitas.', 'danger')
        return redirect(url_for('visitas.lista'))
    
    visita = Visita.query.get_or_404(id)
    
    if request.method == 'POST':
        visita.data_visita = datetime.strptime(request.form.get('data_visita'), '%Y-%m-%d').date()
        visita.empresa_id = request.form.get('empresa_id')
        visita.objetivo = request.form.get('objetivo')
        visita.resumo = request.form.get('resumo')
        visita.proximos_passos = request.form.get('proximos_passos')
        visita.status = request.form.get('status')
        visita.localizacao = request.form.get('localizacao')
        
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='EDITAR_VISITA',
            descricao=f'Editou visita ID {visita.id}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Visita atualizada com sucesso!', 'success')
        return redirect(url_for('visitas.detalhes', id=visita.id))
    
    empresas = Empresa.query.order_by(Empresa.nome).all()
    return render_template('visitas/form.html', visita=visita, empresas=empresas)

@visitas_bp.route('/visitas/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    if not current_user.is_coordenador():
        flash('Você não tem permissão para excluir visitas.', 'danger')
        return redirect(url_for('visitas.lista'))
    
    visita = Visita.query.get_or_404(id)
    
    log = Log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao='EXCLUIR_VISITA',
        descricao=f'Excluiu visita ID {id}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.delete(visita)
    db.session.commit()
    
    flash('Visita excluída com sucesso!', 'success')
    return redirect(url_for('visitas.lista'))
