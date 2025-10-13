from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from routes import admin_bp
from models import db
from models.user import User
from models.log import Log

@admin_bp.route('/admin/usuarios')
@login_required
def usuarios():
    if not current_user.is_admin():
        flash('Apenas administradores podem acessar esta página.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    usuarios = User.query.order_by(User.nome).all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/admin/usuarios/novo', methods=['GET', 'POST'])
@login_required
def novo_usuario():
    if not current_user.is_admin():
        flash('Apenas administradores podem criar usuários.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if User.query.filter_by(email=email).first():
            flash('Já existe um usuário com este email.', 'danger')
            return redirect(url_for('admin.novo_usuario'))
        
        usuario = User(
            nome=request.form.get('nome'),
            email=email,
            perfil=request.form.get('perfil'),
            ativo=request.form.get('ativo') == 'on'
        )
        usuario.set_password(request.form.get('senha'))
        
        db.session.add(usuario)
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='CRIAR_USUARIO',
            descricao=f'Criou usuário {usuario.email} com perfil {usuario.perfil}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Usuário {usuario.nome} criado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', usuario=None)

@admin_bp.route('/admin/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if not current_user.is_admin():
        flash('Apenas administradores podem editar usuários.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    usuario = User.query.get_or_404(id)
    
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.perfil = request.form.get('perfil')
        usuario.ativo = request.form.get('ativo') == 'on'
        
        senha = request.form.get('senha')
        if senha:
            usuario.set_password(senha)
        
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='EDITAR_USUARIO',
            descricao=f'Editou usuário {usuario.email}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Usuário {usuario.nome} atualizado com sucesso!', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', usuario=usuario)

@admin_bp.route('/admin/usuarios/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_usuario(id):
    if not current_user.is_admin():
        flash('Apenas administradores podem excluir usuários.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if id == current_user.id:
        flash('Você não pode excluir seu próprio usuário.', 'danger')
        return redirect(url_for('admin.usuarios'))
    
    usuario = User.query.get_or_404(id)
    nome = usuario.nome
    
    log = Log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao='EXCLUIR_USUARIO',
        descricao=f'Excluiu usuário {usuario.email}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.delete(usuario)
    db.session.commit()
    
    flash(f'Usuário {nome} excluído com sucesso!', 'success')
    return redirect(url_for('admin.usuarios'))
