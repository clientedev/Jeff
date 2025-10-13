from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from routes import importacao_bp
from models import db
from models.empresa import Empresa
from models.visita import Visita
from models.demanda import Demanda
from models.user import User
from models.log import Log
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@importacao_bp.route('/importacao')
@login_required
def index():
    if not current_user.is_atendente():
        flash('Você não tem permissão para importar dados.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('importacao/index.html')

@importacao_bp.route('/importacao/empresas', methods=['GET', 'POST'])
@login_required
def importar_empresas():
    if not current_user.is_atendente():
        flash('Você não tem permissão para importar empresas.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo foi enviado.', 'danger')
            return redirect(request.url)
        
        file = request.files['arquivo']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                df = pd.read_excel(file)
                
                required_columns = ['nome']
                if not all(col in df.columns for col in required_columns):
                    flash(f'O arquivo deve conter as colunas: {", ".join(required_columns)}', 'danger')
                    return redirect(request.url)
                
                importadas = 0
                erros = []
                
                for index, row in df.iterrows():
                    try:
                        empresa_existente = Empresa.query.filter_by(cnpj=row.get('cnpj')).first() if pd.notna(row.get('cnpj')) else None
                        
                        if empresa_existente:
                            erros.append(f'Linha {index + 2}: CNPJ {row.get("cnpj")} já existe')
                            continue
                        
                        empresa = Empresa(
                            nome=row['nome'],
                            cnpj=row.get('cnpj') if pd.notna(row.get('cnpj')) else None,
                            ie=row.get('ie') if pd.notna(row.get('ie')) else None,
                            segmento=row.get('segmento') if pd.notna(row.get('segmento')) else None,
                            porte=row.get('porte') if pd.notna(row.get('porte')) else None,
                            endereco=row.get('endereco') if pd.notna(row.get('endereco')) else None,
                            cidade=row.get('cidade') if pd.notna(row.get('cidade')) else None,
                            uf=row.get('uf') if pd.notna(row.get('uf')) else None,
                            contato_principal=row.get('contato_principal') if pd.notna(row.get('contato_principal')) else None,
                            telefone=row.get('telefone') if pd.notna(row.get('telefone')) else None,
                            email=row.get('email') if pd.notna(row.get('email')) else None,
                            status=row.get('status', 'Ativo') if pd.notna(row.get('status')) else 'Ativo',
                            observacoes=row.get('observacoes') if pd.notna(row.get('observacoes')) else None,
                            responsavel=row.get('responsavel') if pd.notna(row.get('responsavel')) else None
                        )
                        db.session.add(empresa)
                        importadas += 1
                    except Exception as e:
                        erros.append(f'Linha {index + 2}: {str(e)}')
                
                db.session.commit()
                
                log = Log(
                    usuario_id=current_user.id,
                    usuario_email=current_user.email,
                    acao='Importação de empresas',
                    descricao=f'Importadas {importadas} empresas via Excel',
                    ip_address=request.remote_addr
                )
                db.session.add(log)
                db.session.commit()
                
                flash(f'{importadas} empresas importadas com sucesso!', 'success')
                if erros:
                    flash(f'Erros encontrados: {len(erros)}. Primeira ocorrência: {erros[0]}', 'warning')
                
                return redirect(url_for('empresas.lista'))
                
            except Exception as e:
                flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Formato de arquivo não permitido. Use .xlsx ou .xls', 'danger')
            return redirect(request.url)
    
    return render_template('importacao/empresas.html')

@importacao_bp.route('/importacao/visitas', methods=['GET', 'POST'])
@login_required
def importar_visitas():
    if not current_user.is_atendente():
        flash('Você não tem permissão para importar visitas.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo foi enviado.', 'danger')
            return redirect(request.url)
        
        file = request.files['arquivo']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                df = pd.read_excel(file)
                
                required_columns = ['data_visita', 'empresa_cnpj', 'responsavel_email']
                if not all(col in df.columns for col in required_columns):
                    flash(f'O arquivo deve conter as colunas: {", ".join(required_columns)}', 'danger')
                    return redirect(request.url)
                
                importadas = 0
                erros = []
                
                for index, row in df.iterrows():
                    try:
                        empresa = Empresa.query.filter_by(cnpj=row['empresa_cnpj']).first()
                        if not empresa:
                            erros.append(f'Linha {index + 2}: Empresa com CNPJ {row["empresa_cnpj"]} não encontrada')
                            continue
                        
                        responsavel = User.query.filter_by(email=row['responsavel_email']).first()
                        if not responsavel:
                            erros.append(f'Linha {index + 2}: Usuário {row["responsavel_email"]} não encontrado')
                            continue
                        
                        data_visita = pd.to_datetime(row['data_visita']).date()
                        
                        visita = Visita(
                            data_visita=data_visita,
                            empresa_id=empresa.id,
                            responsavel_id=responsavel.id,
                            objetivo=row.get('objetivo') if pd.notna(row.get('objetivo')) else None,
                            resumo=row.get('resumo') if pd.notna(row.get('resumo')) else None,
                            proximos_passos=row.get('proximos_passos') if pd.notna(row.get('proximos_passos')) else None,
                            status=row.get('status', 'Planejada') if pd.notna(row.get('status')) else 'Planejada',
                            localizacao=row.get('localizacao') if pd.notna(row.get('localizacao')) else None
                        )
                        db.session.add(visita)
                        importadas += 1
                    except Exception as e:
                        erros.append(f'Linha {index + 2}: {str(e)}')
                
                db.session.commit()
                
                log = Log(
                    usuario_id=current_user.id,
                    usuario_email=current_user.email,
                    acao='Importação de visitas',
                    descricao=f'Importadas {importadas} visitas via Excel',
                    ip_address=request.remote_addr
                )
                db.session.add(log)
                db.session.commit()
                
                flash(f'{importadas} visitas importadas com sucesso!', 'success')
                if erros:
                    flash(f'Erros encontrados: {len(erros)}. Primeira ocorrência: {erros[0]}', 'warning')
                
                return redirect(url_for('visitas.lista'))
                
            except Exception as e:
                flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Formato de arquivo não permitido. Use .xlsx ou .xls', 'danger')
            return redirect(request.url)
    
    return render_template('importacao/visitas.html')

@importacao_bp.route('/importacao/demandas', methods=['GET', 'POST'])
@login_required
def importar_demandas():
    if not current_user.is_atendente():
        flash('Você não tem permissão para importar demandas.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo foi enviado.', 'danger')
            return redirect(request.url)
        
        file = request.files['arquivo']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                df = pd.read_excel(file)
                
                required_columns = ['empresa_cnpj', 'tipo', 'descricao']
                if not all(col in df.columns for col in required_columns):
                    flash(f'O arquivo deve conter as colunas: {", ".join(required_columns)}', 'danger')
                    return redirect(request.url)
                
                importadas = 0
                erros = []
                
                for index, row in df.iterrows():
                    try:
                        empresa = Empresa.query.filter_by(cnpj=row['empresa_cnpj']).first()
                        if not empresa:
                            erros.append(f'Linha {index + 2}: Empresa com CNPJ {row["empresa_cnpj"]} não encontrada')
                            continue
                        
                        responsavel = None
                        if pd.notna(row.get('responsavel_email')):
                            responsavel = User.query.filter_by(email=row['responsavel_email']).first()
                        
                        demanda = Demanda(
                            empresa_id=empresa.id,
                            tipo=row['tipo'],
                            descricao=row['descricao'],
                            setor_responsavel=row.get('setor_responsavel') if pd.notna(row.get('setor_responsavel')) else None,
                            status=row.get('status', 'Nova') if pd.notna(row.get('status')) else 'Nova',
                            valor_estimado=float(row.get('valor_estimado', 0)) if pd.notna(row.get('valor_estimado')) else 0.0,
                            responsavel_id=responsavel.id if responsavel else None,
                            historico=row.get('historico') if pd.notna(row.get('historico')) else None
                        )
                        db.session.add(demanda)
                        importadas += 1
                    except Exception as e:
                        erros.append(f'Linha {index + 2}: {str(e)}')
                
                db.session.commit()
                
                log = Log(
                    usuario_id=current_user.id,
                    usuario_email=current_user.email,
                    acao='Importação de demandas',
                    descricao=f'Importadas {importadas} demandas via Excel',
                    ip_address=request.remote_addr
                )
                db.session.add(log)
                db.session.commit()
                
                flash(f'{importadas} demandas importadas com sucesso!', 'success')
                if erros:
                    flash(f'Erros encontrados: {len(erros)}. Primeira ocorrência: {erros[0]}', 'warning')
                
                return redirect(url_for('demandas.lista'))
                
            except Exception as e:
                flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Formato de arquivo não permitido. Use .xlsx ou .xls', 'danger')
            return redirect(request.url)
    
    return render_template('importacao/demandas.html')

@importacao_bp.route('/importacao/template/<tipo>')
@login_required
def download_template(tipo):
    templates = {
        'empresas': {
            'colunas': ['nome', 'cnpj', 'ie', 'segmento', 'porte', 'endereco', 'cidade', 'uf', 
                       'contato_principal', 'telefone', 'email', 'status', 'observacoes', 'responsavel'],
            'exemplo': ['Empresa Exemplo LTDA', '12.345.678/0001-90', '123.456.789', 'Metalúrgica', 
                       'Médio', 'Rua das Flores, 123', 'São Paulo', 'SP', 'João Silva', 
                       '(11) 98765-4321', 'contato@empresa.com', 'Ativo', 'Observações gerais', 'Consultor X']
        },
        'visitas': {
            'colunas': ['data_visita', 'empresa_cnpj', 'responsavel_email', 'objetivo', 'resumo', 
                       'proximos_passos', 'status', 'localizacao'],
            'exemplo': ['2025-10-15', '12.345.678/0001-90', 'consultor@senai.com', 
                       'Diagnóstico inicial', 'Visita realizada com sucesso', 
                       'Agendar próxima visita', 'Realizada', 'Fábrica - Setor de Produção']
        },
        'demandas': {
            'colunas': ['empresa_cnpj', 'tipo', 'descricao', 'setor_responsavel', 'status', 
                       'valor_estimado', 'responsavel_email', 'historico'],
            'exemplo': ['12.345.678/0001-90', 'Consultoria', 'Implementação de 5S', 
                       'Produção', 'Nova', '15000.00', 'consultor@senai.com', 'Demanda identificada em visita']
        }
    }
    
    if tipo not in templates:
        flash('Tipo de template inválido.', 'danger')
        return redirect(url_for('importacao.index'))
    
    template_data = templates[tipo]
    df = pd.DataFrame([template_data['exemplo']], columns=template_data['colunas'])
    
    output_path = f'/tmp/template_{tipo}.xlsx'
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    from flask import send_file
    return send_file(output_path, as_attachment=True, download_name=f'template_{tipo}.xlsx')
