from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.inovacao import InovacaoEmpresa
from models.visita import Visita
from models.diagnostico import Diagnostico
from sqlalchemy import func
from datetime import datetime

consultores_bp = Blueprint('consultores', __name__, url_prefix='/consultores')

@consultores_bp.route('/')
@login_required
def index():
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    consultores = User.query.filter(
        User.perfil.in_(['Consultor', 'Coordenador'])
    ).all()
    
    total_consultores = len(consultores)
    consultores_ativos = len([c for c in consultores if c.ativo])
    
    stats = []
    for consultor in consultores:
        total_visitas = Visita.query.filter_by(responsavel_id=consultor.id).count()
        total_inovacoes = InovacaoEmpresa.query.filter_by(consultor_id=consultor.id).count()
        total_diagnosticos = Diagnostico.query.filter_by(consultor_id=consultor.id).count()
        
        stats.append({
            'consultor': consultor,
            'visitas': total_visitas,
            'inovacoes': total_inovacoes,
            'diagnosticos': total_diagnosticos
        })
    
    return render_template('consultores/index.html',
                         consultores=consultores,
                         total_consultores=total_consultores,
                         consultores_ativos=consultores_ativos,
                         stats=stats)

@consultores_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('consultores.index'))
    
    if request.method == 'POST':
        email = request.form['email']
        
        if User.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'danger')
            return redirect(url_for('consultores.novo'))
        
        consultor = User(
            nome=request.form['nome'],
            email=email,
            perfil=request.form.get('perfil', 'Consultor'),
            telefone=request.form.get('telefone'),
            especialidade=request.form.get('especialidade'),
            bio=request.form.get('bio'),
            ativo=True
        )
        senha = request.form.get('senha')
        if not senha:
            flash('Senha é obrigatória para novo consultor.', 'danger')
            return redirect(url_for('consultores.novo'))
        consultor.set_password(senha)
        
        db.session.add(consultor)
        db.session.commit()
        
        flash(f'Consultor {consultor.nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('consultores.index'))
    
    return render_template('consultores/form.html')

@consultores_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('consultores.index'))
    
    consultor = User.query.get_or_404(id)
    
    if request.method == 'POST':
        consultor.nome = request.form['nome']
        consultor.email = request.form['email']
        consultor.perfil = request.form.get('perfil', consultor.perfil)
        consultor.telefone = request.form.get('telefone')
        consultor.especialidade = request.form.get('especialidade')
        consultor.bio = request.form.get('bio')
        consultor.ativo = request.form.get('ativo') == 'on'
        
        if request.form.get('senha'):
            consultor.set_password(request.form['senha'])
        
        db.session.commit()
        flash('Consultor atualizado com sucesso!', 'success')
        return redirect(url_for('consultores.index'))
    
    return render_template('consultores/form.html', consultor=consultor)

@consultores_bp.route('/<int:id>')
@login_required
def detalhes(id):
    consultor = User.query.get_or_404(id)
    
    visitas = Visita.query.filter_by(responsavel_id=id).order_by(Visita.data_visita.desc()).limit(10).all()
    inovacoes = InovacaoEmpresa.query.filter_by(consultor_id=id).order_by(InovacaoEmpresa.data_atribuicao.desc()).limit(10).all()
    diagnosticos = Diagnostico.query.filter_by(consultor_id=id).order_by(Diagnostico.data_diagnostico.desc()).limit(10).all()
    
    return render_template('consultores/detalhes.html',
                         consultor=consultor,
                         visitas=visitas,
                         inovacoes=inovacoes,
                         diagnosticos=diagnosticos)
