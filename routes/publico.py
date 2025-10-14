from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.empresa import Empresa
from models.demanda import Demanda
from datetime import datetime

publico_bp = Blueprint('publico', __name__, url_prefix='/publico')

@publico_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro_empresa():
    if request.method == 'POST':
        try:
            empresa = Empresa(
                nome=request.form.get('nome'),
                cnpj=request.form.get('cnpj'),
                segmento=request.form.get('segmento'),
                porte=request.form.get('porte'),
                endereco=request.form.get('endereco'),
                cidade=request.form.get('cidade'),
                uf=request.form.get('uf'),
                contato_principal=request.form.get('contato_principal'),
                telefone=request.form.get('telefone'),
                email=request.form.get('email'),
                status='Ativo',
                observacoes='Cadastro via formulario publico',
                responsavel='Sistema'
            )
            
            db.session.add(empresa)
            db.session.flush()
            
            if request.form.get('demanda_descricao'):
                demanda = Demanda(
                    empresa_id=empresa.id,
                    titulo=request.form.get('demanda_titulo', 'Demanda inicial'),
                    descricao=request.form.get('demanda_descricao'),
                    tipo=request.form.get('demanda_tipo', 'Consultoria'),
                    status='Aberta',
                    prioridade=request.form.get('prioridade', 'Media'),
                    data_abertura=datetime.now().date()
                )
                db.session.add(demanda)
            
            db.session.commit()
            
            return render_template('publico/sucesso.html', empresa=empresa)
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao processar cadastro: {str(e)}', 'danger')
            return redirect(url_for('publico.cadastro_empresa'))
    
    return render_template('publico/cadastro.html')

@publico_bp.route('/sucesso')
def sucesso():
    return render_template('publico/sucesso.html')
