from app import app, db
from models.user import User

with app.app_context():
    db.create_all()
    
    admin_user = User.query.filter_by(email='admin@senai.com').first()
    if not admin_user:
        admin_user = User(
            nome='Administrador',
            email='admin@senai.com',
            perfil='Administrador',
            ativo=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print('Usuário admin criado: admin@senai.com / admin123')
