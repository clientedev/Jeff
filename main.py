from app import app, db
from models.user import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    with app.app_context():
        logger.info("Criando tabelas do banco de dados...")
        db.create_all()
        logger.info("Tabelas criadas com sucesso!")
        
        admin_user = User.query.filter_by(email='admin@senai.com').first()
        if not admin_user:
            logger.info("Criando usuário admin...")
            admin_user = User(
                nome='Administrador',
                email='admin@senai.com',
                perfil='Administrador',
                ativo=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            logger.info('Usuário admin criado: admin@senai.com / admin123')
        else:
            logger.info('Usuário admin já existe.')
except Exception as e:
    logger.error(f"Erro durante inicialização: {e}")
    raise
