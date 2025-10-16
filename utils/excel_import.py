import pandas as pd
from datetime import datetime
from models import db
from models.proposta import Proposta
from models.cronograma_atividade import CronogramaAtividade
from models.produtividade import Produtividade
from models.faturamento import Faturamento
from models.controle_sgt import ControleSGT
from models.relatorio_sebrae import RelatorioSebrae
from models.prospeccao import Prospeccao
from models.followup import FollowUp
import logging

logger = logging.getLogger(__name__)

def parse_date(date_value):
    if pd.isna(date_value) or date_value is None:
        return None
    if isinstance(date_value, datetime):
        return date_value.date()
    if isinstance(date_value, str):
        try:
            return datetime.strptime(date_value, '%Y-%m-%d').date()
        except:
            try:
                return datetime.strptime(date_value, '%d/%m/%Y').date()
            except:
                return None
    return None

def parse_float(value):
    if pd.isna(value) or value is None:
        return None
    try:
        return float(value)
    except:
        return None

def parse_int(value):
    if pd.isna(value) or value is None:
        return None
    try:
        return int(value)
    except:
        return None

def importar_cronograma_propostas(file_path):
    logger.info(f"Importando propostas de {file_path}")
    
    try:
        df = pd.read_excel(file_path, sheet_name='CONSULTA INFO.')
        
        count_inserted = 0
        count_updated = 0
        
        for _, row in df.iterrows():
            numero_proposta = str(row.get('PROPOSTA', '')).strip()
            
            if not numero_proposta or numero_proposta == 'nan':
                continue
            
            proposta = Proposta.query.filter_by(numero_proposta=numero_proposta).first()
            
            is_new = False
            if not proposta:
                proposta = Proposta(numero_proposta=numero_proposta)
                is_new = True
                count_inserted += 1
            else:
                count_updated += 1
            
            proposta.empresa_nome = str(row.get('EMPRESA', ''))
            proposta.cnpj = str(row.get('CNPJ', '')) if not pd.isna(row.get('CNPJ')) else None
            proposta.sigla = str(row.get('SIGLA', '')) if not pd.isna(row.get('SIGLA')) else None
            proposta.er = str(row.get('ER', '')) if not pd.isna(row.get('ER')) else None
            proposta.porte = str(row.get('PORTE', '')) if not pd.isna(row.get('PORTE')) else None
            proposta.solucao = str(row.get('SOLUÇÃO', '')) if not pd.isna(row.get('SOLUÇÃO')) else None
            proposta.horas = parse_int(row.get('HORAS'))
            proposta.consultor_principal = str(row.get('CONSULTOR 1', '')) if not pd.isna(row.get('CONSULTOR 1')) else None
            proposta.data_inicio = parse_date(row.get('INÍCIO'))
            proposta.data_termino = parse_date(row.get('TÉRMINO'))
            proposta.endereco = str(row.get('ENDEREÇO', '')) if not pd.isna(row.get('ENDEREÇO')) else None
            proposta.regiao = str(row.get('REGIÃO', '')) if not pd.isna(row.get('REGIÃO')) else None
            municipio_val = str(row.get('MUNICÍPIO', '')) if not pd.isna(row.get('MUNICÍPIO')) else None
            uf_val = str(row.get('UF', '')) if not pd.isna(row.get('UF')) else None
            
            if uf_val and len(uf_val) > 2:
                proposta.municipio = uf_val
                proposta.uf = municipio_val if municipio_val and len(municipio_val) <= 2 else None
            else:
                proposta.municipio = municipio_val
                proposta.uf = uf_val
            proposta.contato = str(row.get('CONTATO', '')) if not pd.isna(row.get('CONTATO')) else None
            proposta.telefone = str(row.get('TELEFONE', '')) if not pd.isna(row.get('TELEFONE')) else None
            proposta.celular = str(row.get('CELULAR', '')) if not pd.isna(row.get('CELULAR')) else None
            
            if is_new:
                db.session.add(proposta)
        
        db.session.commit()
        logger.info(f"Propostas importadas: {count_inserted} inseridas, {count_updated} atualizadas")
        
        return {
            'success': True,
            'inserted': count_inserted,
            'updated': count_updated
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao importar propostas: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def importar_produtividade(file_path):
    logger.info(f"Importando produtividade de {file_path}")
    
    try:
        df = pd.read_excel(file_path, sheet_name='PRODUTIVIDADE')
        
        count = 0
        
        for _, row in df.iterrows():
            consultor = str(row.get('CONSULTOR', '')).strip()
            
            if not consultor or pd.isna(consultor):
                continue
            
            produtividade = Produtividade()
            produtividade.consultor = consultor
            produtividade.horas_trabalhadas = parse_float(row.get('HORAS TRABALHADAS'))
            produtividade.horas_planejadas = parse_float(row.get('HORAS PLANEJADAS'))
            produtividade.percentual_produtividade = parse_float(row.get('PRODUTIVIDADE %'))
            
            if row.get('MÊS'):
                produtividade.mes = parse_int(row.get('MÊS'))
            if row.get('ANO'):
                produtividade.ano = parse_int(row.get('ANO'))
            
            db.session.add(produtividade)
            count += 1
        
        db.session.commit()
        logger.info(f"Produtividade importada: {count} registros")
        
        return {
            'success': True,
            'count': count
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao importar produtividade: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def importar_consideracoes_resumo(file_path):
    logger.info(f"Importando considerações/resumo de {file_path}")
    
    try:
        df = pd.read_excel(file_path, sheet_name='RESUMO')
        
        count_inserted = 0
        count_updated = 0
        
        for _, row in df.iterrows():
            cnpj = str(row.get('CNPJ', '')).strip()
            empresa = str(row.get('EMPRESA', '')).strip()
            
            if not empresa:
                continue
            
            proposta = Proposta.query.filter_by(cnpj=cnpj).first() if cnpj else None
            
            if not proposta and empresa:
                proposta = Proposta.query.filter(Proposta.empresa_nome.ilike(f'%{empresa}%')).first()
            
            if proposta:
                proposta.tipo_programa = str(row.get('TIPO DE PROGRAMA', '')) if not pd.isna(row.get('TIPO DE PROGRAMA')) else None
                proposta.porte = str(row.get('PORTE', '')) if not pd.isna(row.get('PORTE')) else None
                proposta.er = str(row.get('ER', '')) if not pd.isna(row.get('ER')) else None
                proposta.etapa = str(row.get('ETAPA', '')) if not pd.isna(row.get('ETAPA')) else None
                count_updated += 1
            else:
                proposta = Proposta()
                proposta.empresa_nome = empresa
                proposta.cnpj = cnpj if cnpj else None
                proposta.sigla = str(row.get('SIGLA', '')) if not pd.isna(row.get('SIGLA')) else None
                proposta.tipo_programa = str(row.get('TIPO DE PROGRAMA', '')) if not pd.isna(row.get('TIPO DE PROGRAMA')) else None
                proposta.porte = str(row.get('PORTE', '')) if not pd.isna(row.get('PORTE')) else None
                proposta.er = str(row.get('ER', '')) if not pd.isna(row.get('ER')) else None
                proposta.etapa = str(row.get('ETAPA', '')) if not pd.isna(row.get('ETAPA')) else None
                proposta.numero_proposta = f"IMP-{cnpj or empresa[:10]}-{count_inserted}"
                
                db.session.add(proposta)
                count_inserted += 1
        
        db.session.commit()
        logger.info(f"Considerações importadas: {count_inserted} inseridas, {count_updated} atualizadas")
        
        return {
            'success': True,
            'inserted': count_inserted,
            'updated': count_updated
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao importar considerações: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def importar_faturamento(file_path):
    logger.info(f"Importando faturamento de {file_path}")
    
    try:
        df = pd.read_excel(file_path, sheet_name='FATURAMENTO')
        
        count = 0
        
        for _, row in df.iterrows():
            descricao = str(row.get('DESCRIÇÃO', '')).strip()
            valor = parse_float(row.get('VALOR'))
            
            if not descricao or not valor:
                continue
            
            faturamento = Faturamento()
            faturamento.descricao = descricao
            faturamento.valor = valor
            faturamento.data_prevista = parse_date(row.get('DATA PREVISTA'))
            faturamento.data_realizada = parse_date(row.get('DATA REALIZADA'))
            faturamento.status = str(row.get('STATUS', 'Pendente'))
            faturamento.tipo = str(row.get('TIPO', '')) if not pd.isna(row.get('TIPO')) else None
            faturamento.nota_fiscal = str(row.get('NOTA FISCAL', '')) if not pd.isna(row.get('NOTA FISCAL')) else None
            
            db.session.add(faturamento)
            count += 1
        
        db.session.commit()
        logger.info(f"Faturamento importado: {count} registros")
        
        return {
            'success': True,
            'count': count
        }
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao importar faturamento: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
