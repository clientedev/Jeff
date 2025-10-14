from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import db
from models.inovacao import Inovacao, InovacaoEmpresa
from models.empresa import Empresa
from models.user import User
from sqlalchemy import func
from datetime import datetime
import openpyxl
from io import BytesIO

inovacoes_bp = Blueprint('inovacoes', __name__, url_prefix='/inovacoes')

CATEGORIAS_LEAN = [
    '5S - Organização e Limpeza',
    'Kaizen - Melhoria Contínua',
    'Just in Time - Produção Puxada',
    'Kanban - Gestão Visual',
    'Poka-Yoke - Prova de Erros',
    'SMED - Troca Rápida',
    'TPM - Manutenção Produtiva Total',
    'Value Stream Mapping - Mapeamento do Fluxo de Valor',
    'Heijunka - Nivelamento de Produção',
    'Jidoka - Automação Inteligente',
    'Andon - Sinalização de Problemas',
    'Gemba Walk - Gestão no Local',
    'Hoshin Kanri - Desdobramento de Metas',
    'Six Sigma - Redução de Variabilidade',
    'Lean Office - Escritório Enxuto',
    'Outras'
]

@inovacoes_bp.route('/')
@login_required
def index():
    inovacoes = Inovacao.query.filter_by(ativo=True).all()
    
    total_inovacoes = Inovacao.query.count()
    inovacoes_ativas = Inovacao.query.filter_by(ativo=True).count()
    
    total_atribuicoes = InovacaoEmpresa.query.count()
    inovacoes_concluidas = InovacaoEmpresa.query.filter_by(status='Concluída').count()
    inovacoes_em_andamento = InovacaoEmpresa.query.filter_by(status='Em andamento').count()
    inovacoes_planejadas = InovacaoEmpresa.query.filter_by(status='Planejada').count()
    
    por_categoria = db.session.query(
        Inovacao.categoria, 
        func.count(InovacaoEmpresa.id)
    ).join(InovacaoEmpresa).group_by(Inovacao.categoria).all()
    
    empresas_com_inovacoes = db.session.query(
        func.count(func.distinct(InovacaoEmpresa.empresa_id))
    ).scalar() or 0
    
    taxa_conclusao = (inovacoes_concluidas / total_atribuicoes * 100) if total_atribuicoes > 0 else 0
    
    economia_total = db.session.query(func.sum(InovacaoEmpresa.economia_gerada)).scalar() or 0
    investimento_total = db.session.query(func.sum(InovacaoEmpresa.investimento)).scalar() or 0
    roi = ((economia_total - investimento_total) / investimento_total * 100) if investimento_total > 0 else 0
    
    top_empresas = db.session.query(
        Empresa.nome,
        func.count(InovacaoEmpresa.id).label('total'),
        func.sum(InovacaoEmpresa.economia_gerada).label('economia')
    ).join(InovacaoEmpresa).group_by(Empresa.id, Empresa.nome).order_by(func.count(InovacaoEmpresa.id).desc()).limit(10).all()
    
    return render_template('inovacoes/index.html',
                         inovacoes=inovacoes,
                         total_inovacoes=total_inovacoes,
                         inovacoes_ativas=inovacoes_ativas,
                         total_atribuicoes=total_atribuicoes,
                         inovacoes_concluidas=inovacoes_concluidas,
                         inovacoes_em_andamento=inovacoes_em_andamento,
                         inovacoes_planejadas=inovacoes_planejadas,
                         por_categoria=por_categoria,
                         empresas_com_inovacoes=empresas_com_inovacoes,
                         taxa_conclusao=taxa_conclusao,
                         economia_total=economia_total,
                         investimento_total=investimento_total,
                         roi=roi,
                         top_empresas=top_empresas)

@inovacoes_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    if not current_user.is_atendente():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('inovacoes.index'))
    
    if request.method == 'POST':
        inovacao = Inovacao(
            nome=request.form['nome'],
            categoria=request.form['categoria'],
            descricao=request.form.get('descricao'),
            beneficios=request.form.get('beneficios'),
            requisitos=request.form.get('requisitos'),
            tempo_implementacao=request.form.get('tempo_implementacao'),
            nivel_complexidade=request.form.get('nivel_complexidade', 'Média')
        )
        db.session.add(inovacao)
        db.session.commit()
        
        flash('Inovação cadastrada com sucesso!', 'success')
        return redirect(url_for('inovacoes.index'))
    
    return render_template('inovacoes/form.html', categorias=CATEGORIAS_LEAN)

@inovacoes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    if not current_user.is_atendente():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('inovacoes.index'))
    
    inovacao = Inovacao.query.get_or_404(id)
    
    if request.method == 'POST':
        inovacao.nome = request.form['nome']
        inovacao.categoria = request.form['categoria']
        inovacao.descricao = request.form.get('descricao')
        inovacao.beneficios = request.form.get('beneficios')
        inovacao.requisitos = request.form.get('requisitos')
        inovacao.tempo_implementacao = request.form.get('tempo_implementacao')
        inovacao.nivel_complexidade = request.form.get('nivel_complexidade')
        
        db.session.commit()
        flash('Inovação atualizada com sucesso!', 'success')
        return redirect(url_for('inovacoes.index'))
    
    return render_template('inovacoes/form.html', inovacao=inovacao, categorias=CATEGORIAS_LEAN)

@inovacoes_bp.route('/atribuir', methods=['GET', 'POST'])
@login_required
def atribuir():
    if not current_user.is_atendente():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('inovacoes.index'))
    
    if request.method == 'POST':
        atribuicao = InovacaoEmpresa(
            inovacao_id=request.form['inovacao_id'],
            empresa_id=request.form['empresa_id'],
            consultor_id=request.form['consultor_id'],
            status='Planejada',
            data_inicio=datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date() if request.form.get('data_inicio') else None,
            observacoes=request.form.get('observacoes')
        )
        db.session.add(atribuicao)
        db.session.commit()
        
        flash('Inovação atribuída com sucesso!', 'success')
        return redirect(url_for('inovacoes.atribuicoes'))
    
    inovacoes = Inovacao.query.filter_by(ativo=True).all()
    empresas = Empresa.query.filter_by(status='Ativo').all()
    consultores = User.query.filter(User.perfil.in_(['Consultor', 'Coordenador', 'Administrador'])).all()
    
    return render_template('inovacoes/atribuir.html', 
                         inovacoes=inovacoes,
                         empresas=empresas,
                         consultores=consultores)

@inovacoes_bp.route('/atribuicoes')
@login_required
def atribuicoes():
    if current_user.is_consultor() and not current_user.is_atendente():
        atribuicoes = InovacaoEmpresa.query.filter_by(consultor_id=current_user.id).all()
    else:
        atribuicoes = InovacaoEmpresa.query.all()
    
    return render_template('inovacoes/atribuicoes.html', atribuicoes=atribuicoes)

@inovacoes_bp.route('/atribuicao/<int:id>/atualizar', methods=['POST'])
@login_required
def atualizar_atribuicao(id):
    atribuicao = InovacaoEmpresa.query.get_or_404(id)
    
    if not (current_user.is_atendente() or current_user.id == atribuicao.consultor_id):
        flash('Acesso negado.', 'danger')
        return redirect(url_for('inovacoes.atribuicoes'))
    
    atribuicao.status = request.form.get('status', atribuicao.status)
    atribuicao.progresso = int(request.form.get('progresso', atribuicao.progresso))
    atribuicao.observacoes = request.form.get('observacoes', atribuicao.observacoes)
    atribuicao.resultados = request.form.get('resultados', atribuicao.resultados)
    
    if request.form.get('data_conclusao'):
        atribuicao.data_conclusao = datetime.strptime(request.form['data_conclusao'], '%Y-%m-%d').date()
    
    if request.form.get('investimento'):
        atribuicao.investimento = float(request.form['investimento'])
    
    if request.form.get('economia_gerada'):
        atribuicao.economia_gerada = float(request.form['economia_gerada'])
    
    db.session.commit()
    flash('Atribuição atualizada com sucesso!', 'success')
    return redirect(url_for('inovacoes.atribuicoes'))

@inovacoes_bp.route('/api/stats')
@login_required
def api_stats():
    por_status = db.session.query(
        InovacaoEmpresa.status,
        func.count(InovacaoEmpresa.id)
    ).group_by(InovacaoEmpresa.status).all()
    
    return jsonify({
        'por_status': [{'status': s[0], 'count': s[1]} for s in por_status]
    })

@inovacoes_bp.route('/importar', methods=['GET', 'POST'])
@login_required
def importar():
    if not current_user.is_atendente():
        flash('Apenas atendentes podem importar inovacoes.', 'danger')
        return redirect(url_for('inovacoes.index'))
    
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo foi enviado.', 'danger')
            return redirect(url_for('inovacoes.importar'))
        
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(url_for('inovacoes.importar'))
        
        if not arquivo.filename.endswith(('.xlsx', '.xls')):
            flash('Formato invalido. Use arquivos Excel (.xlsx ou .xls).', 'danger')
            return redirect(url_for('inovacoes.importar'))
        
        try:
            wb = openpyxl.load_workbook(arquivo)
            ws = wb.active
            
            importados = 0
            erros = []
            
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    empresa_nome = row[0]
                    inovacao_nome = row[1]
                    data_inicio = row[2]
                    status = row[3] if row[3] else 'Planejada'
                    investimento = float(row[4]) if row[4] else 0
                    economia = float(row[5]) if row[5] else 0
                    
                    if not empresa_nome or not inovacao_nome:
                        erros.append(f'Linha {row_idx}: empresa e inovacao sao obrigatorios')
                        continue
                    
                    empresa = Empresa.query.filter_by(nome=empresa_nome).first()
                    if not empresa:
                        erros.append(f'Linha {row_idx}: empresa "{empresa_nome}" nao encontrada')
                        continue
                    
                    inovacao = Inovacao.query.filter_by(nome=inovacao_nome).first()
                    if not inovacao:
                        erros.append(f'Linha {row_idx}: inovacao "{inovacao_nome}" nao encontrada')
                        continue
                    
                    atribuicao = InovacaoEmpresa(
                        empresa_id=empresa.id,
                        inovacao_id=inovacao.id,
                        consultor_id=current_user.id,
                        data_inicio=data_inicio if isinstance(data_inicio, datetime) else datetime.now().date(),
                        status=status,
                        investimento=investimento,
                        economia_gerada=economia
                    )
                    db.session.add(atribuicao)
                    importados += 1
                    
                except Exception as e:
                    erros.append(f'Linha {row_idx}: {str(e)}')
            
            db.session.commit()
            
            msg = f'{importados} inovacoes importadas com sucesso!'
            if erros:
                msg += f' {len(erros)} erros encontrados.'
            flash(msg, 'success' if not erros else 'warning')
            
            if erros:
                for erro in erros[:5]:
                    flash(erro, 'danger')
            
            return redirect(url_for('inovacoes.atribuicoes'))
            
        except Exception as e:
            flash(f'Erro ao processar arquivo: {str(e)}', 'danger')
            return redirect(url_for('inovacoes.importar'))
    
    return render_template('inovacoes/importar.html')
