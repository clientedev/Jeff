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
    page = request.args.get('page', 1, type=int)
    busca = request.args.get('busca', '')
    
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
    
    empresas = query.order_by(Empresa.nome).paginate(page=page, per_page=20, error_out=False)
    return render_template('empresas/lista.html', empresas=empresas, busca=busca)

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
