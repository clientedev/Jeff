from app import app, db
from utils.excel_import import (
    importar_cronograma_propostas,
    importar_produtividade,
    importar_consideracoes_resumo,
    importar_faturamento
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

files = {
    'cronograma': 'attached_assets/CRONOGRAMA 2.0 (4)_1760629348318.xlsx',
    'controle': 'attached_assets/Controle Geral 3.0_151015_1760629348318.xlsx',
    'consideracoes': 'attached_assets/Controle Geral_Considerações_1760629348318.xlsx'
}

with app.app_context():
    logger.info("=" * 80)
    logger.info("INICIANDO IMPORTAÇÃO DE DADOS")
    logger.info("=" * 80)
    
    logger.info("\n1. Importando Propostas do Cronograma...")
    result = importar_cronograma_propostas(files['cronograma'])
    logger.info(f"Resultado: {result}")
    
    logger.info("\n2. Importando Produtividade...")
    result = importar_produtividade(files['cronograma'])
    logger.info(f"Resultado: {result}")
    
    logger.info("\n3. Importando Considerações/Resumo...")
    result = importar_consideracoes_resumo(files['consideracoes'])
    logger.info(f"Resultado: {result}")
    
    logger.info("\n4. Importando Faturamento...")
    try:
        result = importar_faturamento(files['consideracoes'])
        logger.info(f"Resultado: {result}")
    except Exception as e:
        logger.error(f"Erro ao importar faturamento: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("IMPORTAÇÃO CONCLUÍDA")
    logger.info("=" * 80)
