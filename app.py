from flask import Flask, redirect, url_for
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config
from models import db, login_manager
from routes import auth_bp, dashboard_bp, empresas_bp, visitas_bp, demandas_bp, relatorios_bp, admin_bp
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

csrf = CSRFProtect(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(empresas_bp)
app.register_blueprint(visitas_bp)
app.register_blueprint(demandas_bp)
app.register_blueprint(relatorios_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return redirect(url_for('dashboard.index'))

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/robots.txt')
def robots():
    return '', 204

@app.template_filter('currency')
def currency_filter(value):
    return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        from models.user import User
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
    
    app.run(host='0.0.0.0', port=5000, debug=True)
