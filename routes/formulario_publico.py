from flask import render_template, request, flash, redirect, url_for
from routes import formulario_publico_bp
from models import db
from models.formulario import Formulario, RespostaFormulario
from datetime import datetime

@formulario_publico_bp.route('/f/<token>', methods=['GET', 'POST'])
def preencher(token):
    formulario = Formulario.query.filter_by(token=token).first_or_404()
    
    if not formulario.ativo:
        return render_template('formulario_publico/inativo.html'), 403
    
    if formulario.expira_em and formulario.expira_em < datetime.utcnow():
        return render_template('formulario_publico/expirado.html'), 410
    
    if request.method == 'POST':
        dados_json = {}
        
        for key in request.form.keys():
            if key != 'csrf_token':
                dados_json[key] = request.form.get(key)
        
        resposta = RespostaFormulario(
            formulario_id=formulario.id,
            dados_json=dados_json,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        db.session.add(resposta)
        db.session.commit()
        
        return render_template('formulario_publico/sucesso.html', formulario=formulario)
    
    return render_template('formulario_publico/form.html', formulario=formulario)
