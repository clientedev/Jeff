from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from routes import formularios_bp
from models import db
from models.formulario import Formulario, RespostaFormulario
from models.empresa import Empresa
from models.log import Log
from datetime import datetime, timedelta
import os

@formularios_bp.route('/formularios')
@login_required
def lista():
    formularios = Formulario.query.order_by(Formulario.data_criacao.desc()).all()
    return render_template('formularios/lista.html', formularios=formularios)

@formularios_bp.route('/formularios/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descricao = request.form.get('descricao')
        empresa_id = request.form.get('empresa_id')
        dias_validade = request.form.get('dias_validade', type=int)
        
        expira_em = None
        if dias_validade:
            expira_em = datetime.utcnow() + timedelta(days=dias_validade)
        
        formulario = Formulario(
            titulo=titulo,
            descricao=descricao,
            empresa_id=empresa_id if empresa_id else None,
            criado_por_id=current_user.id,
            expira_em=expira_em
        )
        
        db.session.add(formulario)
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='Criação de formulário',
            descricao=f'Formulário "{titulo}" criado',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Formulário "{titulo}" criado com sucesso!', 'success')
        return redirect(url_for('formularios.detalhes', id=formulario.id))
    
    empresas = Empresa.query.filter_by(status='Ativo').order_by(Empresa.nome).all()
    return render_template('formularios/form.html', empresas=empresas)

@formularios_bp.route('/formularios/<int:id>')
@login_required
def detalhes(id):
    formulario = Formulario.query.get_or_404(id)
    
    base_url = request.url_root.rstrip('/')
    link_publico = f"{base_url}/f/{formulario.token}"
    
    respostas = RespostaFormulario.query.filter_by(formulario_id=id).order_by(
        RespostaFormulario.data_resposta.desc()
    ).all()
    
    return render_template('formularios/detalhes.html', 
                         formulario=formulario,
                         link_publico=link_publico,
                         respostas=respostas)

@formularios_bp.route('/formularios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    formulario = Formulario.query.get_or_404(id)
    
    if request.method == 'POST':
        formulario.titulo = request.form.get('titulo')
        formulario.descricao = request.form.get('descricao')
        formulario.empresa_id = request.form.get('empresa_id') or None
        formulario.ativo = request.form.get('ativo') == 'on'
        
        dias_validade = request.form.get('dias_validade', type=int)
        if dias_validade:
            formulario.expira_em = datetime.utcnow() + timedelta(days=dias_validade)
        
        db.session.commit()
        
        log = Log(
            usuario_id=current_user.id,
            usuario_email=current_user.email,
            acao='Edição de formulário',
            descricao=f'Formulário "{formulario.titulo}" editado',
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Formulário atualizado com sucesso!', 'success')
        return redirect(url_for('formularios.detalhes', id=formulario.id))
    
    empresas = Empresa.query.filter_by(status='Ativo').order_by(Empresa.nome).all()
    return render_template('formularios/form.html', formulario=formulario, empresas=empresas)

@formularios_bp.route('/formularios/<int:id>/excluir', methods=['POST'])
@login_required
def excluir(id):
    if not current_user.is_coordenador():
        flash('Você não tem permissão para excluir formulários.', 'danger')
        return redirect(url_for('formularios.lista'))
    
    formulario = Formulario.query.get_or_404(id)
    titulo = formulario.titulo
    
    db.session.delete(formulario)
    db.session.commit()
    
    log = Log(
        usuario_id=current_user.id,
        usuario_email=current_user.email,
        acao='Exclusão de formulário',
        descricao=f'Formulário "{titulo}" excluído',
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'Formulário "{titulo}" excluído com sucesso!', 'success')
    return redirect(url_for('formularios.lista'))

@formularios_bp.route('/formularios/<int:id>/respostas/<int:resposta_id>')
@login_required
def ver_resposta(id, resposta_id):
    resposta = RespostaFormulario.query.get_or_404(resposta_id)
    return render_template('formularios/resposta.html', resposta=resposta)

@formularios_bp.route('/formularios/<int:id>/processar-resposta/<int:resposta_id>', methods=['POST'])
@login_required
def processar_resposta(id, resposta_id):
    resposta = RespostaFormulario.query.get_or_404(resposta_id)
    formulario = resposta.formulario
    
    if formulario.empresa_id and not resposta.processado:
        empresa = formulario.empresa
        dados = resposta.dados_json
        
        if 'telefone' in dados and not empresa.telefone:
            empresa.telefone = dados['telefone']
        if 'email' in dados and not empresa.email:
            empresa.email = dados['email']
        if 'contato_principal' in dados and not empresa.contato_principal:
            empresa.contato_principal = dados['contato_principal']
        if 'observacoes' in dados:
            if empresa.observacoes:
                empresa.observacoes += f"\n\n[Formulário {formulario.titulo}]\n{dados['observacoes']}"
            else:
                empresa.observacoes = f"[Formulário {formulario.titulo}]\n{dados['observacoes']}"
        
        resposta.processado = True
        db.session.commit()
        
        flash('Resposta processada e dados atualizados na empresa!', 'success')
    else:
        flash('Resposta já foi processada ou formulário não está vinculado a uma empresa.', 'warning')
    
    return redirect(url_for('formularios.detalhes', id=id))
