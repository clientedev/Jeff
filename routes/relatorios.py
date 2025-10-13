from flask import render_template, send_file, request
from flask_login import login_required, current_user
from routes import relatorios_bp
from models.empresa import Empresa
from models.visita import Visita
from models.demanda import Demanda
from models.log import Log
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

@relatorios_bp.route('/relatorios')
@login_required
def index():
    return render_template('relatorios/index.html')

@relatorios_bp.route('/relatorios/empresas/excel')
@login_required
def empresas_excel():
    empresas = Empresa.query.all()
    
    data = []
    for emp in empresas:
        data.append({
            'Nome': emp.nome,
            'CNPJ': emp.cnpj,
            'Segmento': emp.segmento,
            'Cidade': emp.cidade,
            'UF': emp.uf,
            'Status': emp.status,
            'Responsável': emp.responsavel,
            'Data Cadastro': emp.data_cadastro.strftime('%d/%m/%Y') if emp.data_cadastro else ''
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Empresas', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='relatorio_empresas.xlsx'
    )

@relatorios_bp.route('/relatorios/visitas/excel')
@login_required
def visitas_excel():
    visitas = Visita.query.all()
    
    data = []
    for vis in visitas:
        data.append({
            'Data': vis.data_visita.strftime('%d/%m/%Y'),
            'Empresa': vis.empresa.nome if vis.empresa else '',
            'Responsável': vis.responsavel_user.nome if vis.responsavel_user else '',
            'Objetivo': vis.objetivo,
            'Status': vis.status
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Visitas', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='relatorio_visitas.xlsx'
    )

@relatorios_bp.route('/relatorios/demandas/excel')
@login_required
def demandas_excel():
    demandas = Demanda.query.all()
    
    data = []
    for dem in demandas:
        data.append({
            'Empresa': dem.empresa.nome if dem.empresa else '',
            'Tipo': dem.tipo,
            'Status': dem.status,
            'Valor Estimado': dem.valor_estimado,
            'Responsável': dem.responsavel_user.nome if dem.responsavel_user else '',
            'Data Criação': dem.data_criacao.strftime('%d/%m/%Y') if dem.data_criacao else '',
            'Convertida': 'Sim' if dem.convertida_projeto else 'Não'
        })
    
    df = pd.DataFrame(data)
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Demandas', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='relatorio_demandas.xlsx'
    )

@relatorios_bp.route('/relatorios/logs')
@login_required
def logs():
    if not current_user.is_admin():
        return 'Acesso negado', 403
    
    page = request.args.get('page', 1, type=int)
    logs = Log.query.order_by(Log.data_hora.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template('relatorios/logs.html', logs=logs)
