from flask import Blueprint, send_file, flash, redirect, url_for
from flask_login import login_required
from models import db
from models.proposta import Proposta
from models.produtividade import Produtividade
from models.faturamento import Faturamento
import pandas as pd
from io import BytesIO
from datetime import datetime

relatorios_excel_bp = Blueprint('relatorios_excel', __name__, url_prefix='/relatorios-excel')

@relatorios_excel_bp.route('/propostas')
@login_required
def relatorio_propostas():
    propostas = Proposta.query.all()
    
    data = []
    for p in propostas:
        data.append({
            'Número Proposta': p.numero_proposta,
            'Empresa': p.empresa_nome,
            'CNPJ': p.cnpj,
            'Sigla': p.sigla,
            'ER': p.er,
            'Porte': p.porte,
            'Solução': p.solucao,
            'Horas': p.horas,
            'Consultor': p.consultor_principal,
            'Data Início': p.data_inicio.strftime('%d/%m/%Y') if p.data_inicio else '',
            'Data Término': p.data_termino.strftime('%d/%m/%Y') if p.data_termino else '',
            'Status': p.status,
            'Município': p.municipio,
            'UF': p.uf,
            'Valor': p.valor
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Propostas', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'relatorio_propostas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@relatorios_excel_bp.route('/produtividade')
@login_required
def relatorio_produtividade():
    produtividades = Produtividade.query.all()
    
    data = []
    for p in produtividades:
        data.append({
            'Consultor': p.consultor,
            'Mês': p.mes,
            'Ano': p.ano,
            'Horas Trabalhadas': p.horas_trabalhadas,
            'Horas Planejadas': p.horas_planejadas,
            'Produtividade %': p.percentual_produtividade,
            'Nº Propostas': p.numero_propostas,
            'Nº Visitas': p.numero_visitas
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Produtividade', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'relatorio_produtividade_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@relatorios_excel_bp.route('/faturamento')
@login_required
def relatorio_faturamento():
    faturamentos = Faturamento.query.all()
    
    data = []
    for f in faturamentos:
        data.append({
            'Descrição': f.descricao,
            'Valor': f.valor,
            'Data Prevista': f.data_prevista.strftime('%d/%m/%Y') if f.data_prevista else '',
            'Data Realizada': f.data_realizada.strftime('%d/%m/%Y') if f.data_realizada else '',
            'Status': f.status,
            'Tipo': f.tipo,
            'Nota Fiscal': f.nota_fiscal
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Faturamento', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'relatorio_faturamento_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )
