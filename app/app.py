from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from db import db
from models import Usuario, Agendamento
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'd626428838bab4dd0736eb2e79918e0e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db.init_app(app)


# 🔥 CADASTRO + REDIRECIONAMENTO
@app.route('/', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            return render_template(
                'cadastro.html',
                erro='Nome e senha são obrigatórios'
            )

        usuario_existente = Usuario.query.filter_by(nome=nome).first()
        if usuario_existente:
            return render_template(
                'cadastro.html',
                erro='Este nome de usuário já está em uso'
            )

        novo_usuario = Usuario(
            nome=nome,
            senha=generate_password_hash(senha)
        )

        db.session.add(novo_usuario)
        db.session.commit()

        session['usuario_id'] = novo_usuario.id
        session['usuario_nome'] = novo_usuario.nome

        return redirect(url_for('dashboard'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        if not nome or not senha:
            return render_template(
                'login.html',
                erro='Nome e senha são obrigatórios'
            )

        usuario = Usuario.query.filter_by(nome=nome).first()

        senha_armazenada = usuario.senha if usuario else ''
        senha_criptografada = senha_armazenada.startswith(('pbkdf2:', 'scrypt:'))
        senha_valida = (
            check_password_hash(senha_armazenada, senha)
            if senha_criptografada
            else senha_armazenada == senha
        )

        if not usuario or not senha_valida:
            return render_template(
                'login.html',
                erro='Usuário ou senha inválidos'
            )

        session['usuario_id'] = usuario.id
        session['usuario_nome'] = usuario.nome

        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 🔥 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', nome_usuario=session.get('usuario_nome'))


# 🔥 VER TODOS AGENDAMENTOS
@app.route('/agendamentos', methods=['GET'])
def ver_agendamentos():
    if 'usuario_id' not in session:
        return jsonify({"message": "Não autenticado"}), 401

    agendamentos = Agendamento.query.filter_by(
        agendamento_user=session['usuario_id']
    ).all()

    return jsonify({
        "agendamentos": [a.to_dict() for a in agendamentos]
    }), 200


# 🔥 VER UM AGENDAMENTO
@app.route('/agendamentos/<int:agendamento_id>', methods=['GET'])
def ver_agendamento_especifico(agendamento_id):
    if 'usuario_id' not in session:
        return jsonify({"message": "Não autenticado"}), 401

    agendamento = Agendamento.query.filter_by(
        id=agendamento_id,
        agendamento_user=session['usuario_id']
    ).first()

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    return jsonify({
        "agendamento": agendamento.to_dict()
    }), 200


# 🔥 CRIAR AGENDAMENTO
@app.route('/criar-agendamento', methods=['POST'])
def criar_agendar():
    if 'usuario_id' not in session:
        return jsonify({"message": "Não autenticado"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"message": "Nenhum dado enviado"}), 400

    titulo = data.get('titulo')
    descricao = data.get('descricao')
    status = data.get('status', 0)
    if not titulo:
        return jsonify({"message": "Título é obrigatório"}), 400

    novo_agendamento = Agendamento(
        titulo=titulo,
        descricao=descricao,
        status=status,
        agendamento_user=session['usuario_id']
    )

    db.session.add(novo_agendamento)
    db.session.commit()

    return jsonify({
        "message": "Criado com sucesso",
        "agendamento": novo_agendamento.to_dict()
    }), 201


# 🔥 ATUALIZAR AGENDAMENTO
@app.route('/agendamentos/<int:agendamento_id>', methods=['PUT'])
def atualizar_agendamento(agendamento_id):
    if 'usuario_id' not in session:
        return jsonify({"message": "Não autenticado"}), 401

    agendamento = Agendamento.query.filter_by(
        id=agendamento_id,
        agendamento_user=session['usuario_id']
    ).first()

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Nenhum dado enviado"}), 400

    agendamento.titulo = data.get('titulo', agendamento.titulo)
    agendamento.descricao = data.get('descricao', agendamento.descricao)
    agendamento.status = data.get('status', agendamento.status)
    db.session.commit()

    return jsonify({"message": "Atualizado com sucesso"}), 200


# 🔥 DELETAR AGENDAMENTO
@app.route('/agendamentos/<int:agendamento_id>', methods=['DELETE'])
def remover_agendamento(agendamento_id):
    if 'usuario_id' not in session:
        return jsonify({"message": "Não autenticado"}), 401

    agendamento = Agendamento.query.filter_by(
        id=agendamento_id,
        agendamento_user=session['usuario_id']
    ).first()

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    db.session.delete(agendamento)
    db.session.commit()

    return jsonify({"message": "Deletado com sucesso"}), 200


# 🔥 START APP
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)