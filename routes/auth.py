from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from routes import auth_bp
from models import db
from models.user import User
from models.log import Log
from datetime import datetime

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(senha):
            if not user.ativo:
                flash('Sua conta está inativa. Entre em contato com o administrador.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=True)
            user.ultimo_acesso = datetime.utcnow()
            db.session.commit()
            
            log = Log(
                usuario_id=user.id,
                usuario_email=user.email,
                acao='LOGIN',
                descricao=f'Usuário {user.nome} realizou login',
                ip_address=request.remote_addr
            )
            db.session.add(log)
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard.index'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='LOGOUT',
            descricao=f'Usuário {current_user.nome} realizou logout',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('auth.login'))
