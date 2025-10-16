from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
import os
from utils.excel_import import (
    importar_cronograma_propostas,
    importar_produtividade,
    importar_consideracoes_resumo,
    importar_faturamento
)

excel_import_bp = Blueprint('excel_import', __name__, url_prefix='/excel-import')

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@excel_import_bp.route('/')
@login_required
def index():
    return render_template('excel_import/index.html')

@excel_import_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('excel_import.index'))
    
    file = request.files['file']
    tipo_importacao = request.form.get('tipo_importacao')
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('excel_import.index'))
    
    if not allowed_file(file.filename):
        flash('Formato de arquivo inválido. Use apenas .xlsx ou .xls', 'danger')
        return redirect(url_for('excel_import.index'))
    
    filename = secure_filename(file.filename)
    upload_folder = 'static/uploads/temp'
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    
    result = None
    
    try:
        if tipo_importacao == 'cronograma':
            result = importar_cronograma_propostas(filepath)
        elif tipo_importacao == 'produtividade':
            result = importar_produtividade(filepath)
        elif tipo_importacao == 'consideracoes':
            result = importar_consideracoes_resumo(filepath)
        elif tipo_importacao == 'faturamento':
            result = importar_faturamento(filepath)
        else:
            flash('Tipo de importação não reconhecido', 'danger')
            return redirect(url_for('excel_import.index'))
        
        if result.get('success'):
            msg = f"Importação concluída com sucesso! "
            if 'inserted' in result:
                msg += f"{result['inserted']} registros inseridos, {result['updated']} atualizados."
            elif 'count' in result:
                msg += f"{result['count']} registros importados."
            flash(msg, 'success')
        else:
            flash(f"Erro na importação: {result.get('error', 'Erro desconhecido')}", 'danger')
            
    except Exception as e:
        flash(f"Erro ao processar arquivo: {str(e)}", 'danger')
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
    
    return redirect(url_for('excel_import.index'))

@excel_import_bp.route('/auto-import')
@login_required
def auto_import():
    files = {
        'cronograma': 'attached_assets/CRONOGRAMA 2.0 (4)_1760629348318.xlsx',
        'controle': 'attached_assets/Controle Geral 3.0_151015_1760629348318.xlsx',
        'consideracoes': 'attached_assets/Controle Geral_Considerações_1760629348318.xlsx'
    }
    
    results = []
    
    if os.path.exists(files['cronograma']):
        result = importar_cronograma_propostas(files['cronograma'])
        results.append(f"Cronograma: {result}")
    
    if os.path.exists(files['cronograma']):
        result = importar_produtividade(files['cronograma'])
        results.append(f"Produtividade: {result}")
    
    if os.path.exists(files['consideracoes']):
        result = importar_consideracoes_resumo(files['consideracoes'])
        results.append(f"Considerações: {result}")
    
    if os.path.exists(files['consideracoes']):
        result = importar_faturamento(files['consideracoes'])
        results.append(f"Faturamento: {result}")
    
    flash(f"Importação automática concluída! {len(results)} arquivos processados.", 'success')
    return redirect(url_for('excel_import.index'))
