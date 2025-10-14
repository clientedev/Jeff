from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from routes import empresas_bp
from models import db
from models.empresa import Empresa
from models.log import Log
from werkzeug.utils import secure_filename
import os

@empresas_bp.route('/empresas')
@login_required
def lista():
    from sqlalchemy import func
    
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    porte = request.args.get('porte', '')
    status = request.args.get('status', '')
    uf = request.args.get('uf', '')
    segmento = request.args.get('segmento', '')
    
    query = Empresa.query
    
    if busca:
        query = query.filter(
            db.or_(
                Empresa.nome.ilike(f'%{busca}%'),
                Empresa.cnpj.ilike(f'%{busca}%'),
                Empresa.cidade.ilike(f'%{busca}%'),
                Empresa.segmento.ilike(f'%{busca}%')
            )
        )
    
    if porte:
        query = query.filter(Empresa.porte == porte)
    
    if status:
        query = query.filter(Empresa.status == status)
    
    if uf:
        query = query.filter(Empresa.uf == uf)
    
    if segmento:
        query = query.filter(Empresa.segmento.ilike(f'%{segmento}%'))
    
    empresas = query.order_by(Empresa.nome).paginate(page=page, per_page=20, error_out=False)
    
    total_empresas = Empresa.query.count()
    empresas_ativas = Empresa.query.filter_by(status='Ativo').count()
    
    por_porte = db.session.query(
        Empresa.porte,
        func.count(Empresa.id)
    ).group_by(Empresa.porte).all()
    
    por_uf = db.session.query(
        Empresa.uf,
        func.count(Empresa.id)
    ).group_by(Empresa.uf).order_by(func.count(Empresa.id).desc()).limit(10).all()
    
    todos_ufs = db.session.query(Empresa.uf).distinct().order_by(Empresa.uf).all()
    todos_portes = db.session.query(Empresa.porte).distinct().order_by(Empresa.porte).all()
    todos_segmentos = db.session.query(Empresa.segmento).distinct().order_by(Empresa.segmento).all()
    
    return render_template('empresas/lista.html', 
                         empresas=empresas, 
                         busca=busca,
                         porte=porte,
                         status=status,
                         uf=uf,
                         segmento=segmento,
                         total_empresas=total_empresas,
                         empresas_ativas=empresas_ativas,
                         por_porte=por_porte,
                         por_uf=por_uf,
                         todos_ufs=[u[0] for u in todos_ufs if u[0]],
                         todos_portes=[p[0] for p in todos_portes if p[0]],
                         todos_segmentos=[s[0] for s in todos_segmentos if s[0]])

@empresas_bp.route('/empresas/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if not current_user.is_atendente():
        flash('Você não tem permissão para criar empresas.', 'danger')
        return redirect(url_for('empresas.lista'))
    
    if request.method == 'POST':
        empresa = Empresa(
            nome=request.form.get('nome'),
            cnpj=request.form.get('cnpj'),
            ie=request.form.get('ie'),
            segmento=request.form.get('segmento'),
            porte=request.form.get('porte'),
            endereco=request.form.get('endereco'),
            cidade=request.form.get('cidade'),
            uf=request.form.get('uf'),
            contato_principal=request.form.get('contato_principal'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            status=request.form.get('status', 'Ativo'),
            observacoes=request.form.get('observacoes'),
            responsavel=current_user.nome
        )
        
        db.session.add(empresa)
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='CRIAR_EMPRESA',
            descricao=f'Criou empresa {empresa.nome}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Empresa {empresa.nome} cadastrada com sucesso!', 'success')
        return redirect(url_for('empresas.lista'))
    
    return render_template('empresas/form.html', empresa=None)

@empresas_bp.route('/empresas/<int:id>')
@login_required
def detalhes(id):
    empresa = Empresa.query.get_or_404(id)
    return render_template('empresas/detalhes.html', empresa=empresa)

@empresas_bp.route('/empresas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not current_user.is_atendente():
        flash('Você não tem permissão para editar empresas.', 'danger')
        return redirect(url_for('empresas.lista'))
    
    empresa = Empresa.query.get_or_404(id)
    
    if request.method == 'POST':
        empresa.nome = request.form.get('nome')
        empresa.cnpj = request.form.get('cnpj')
        empresa.ie = request.form.get('ie')
        empresa.segmento = request.form.get('segmento')
        empresa.porte = request.form.get('porte')
        empresa.endereco = request.form.get('endereco')
        empresa.cidade = request.form.get('cidade')
        empresa.uf = request.form.get('uf')
        empresa.contato_principal = request.form.get('contato_principal')
        empresa.telefone = request.form.get('telefone')
        empresa.email = request.form.get('email')
        empresa.status = request.form.get('status')
        empresa.observacoes = request.form.get('observacoes')
        
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='EDITAR_EMPRESA',
            descricao=f'Editou empresa {empresa.nome}',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Empresa {empresa.nome} atualizada com sucesso!', 'success')
        return redirect(url_for('empresas.detalhes', id=empresa.id))
    
    return render_template('empresas/form.html', empresa=empresa)

@empresas_bp.route('/empresas/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    if not current_user.is_coordenador():
        flash('Você não tem permissão para excluir empresas.', 'danger')
        return redirect(url_for('empresas.lista'))
    
    empresa = Empresa.query.get_or_404(id)
    nome = empresa.nome
    
    log = Log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao='EXCLUIR_EMPRESA',
        descricao=f'Excluiu empresa {nome}',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    
    db.session.delete(empresa)
    db.session.commit()
    
    flash(f'Empresa {nome} excluída com sucesso!', 'success')
    return redirect(url_for('empresas.lista'))
