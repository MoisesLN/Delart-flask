from flask import Flask, jsonify, request, render_template, redirect, url_for
from db import db
from models import Usuario, Agendamento

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

        # (opcional) salvar usuário no banco depois
        # novo_usuario = Usuario(nome=nome, senha=senha)
        # db.session.add(novo_usuario)
        # db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template('cadastro.html')


# 🔥 DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


# 🔥 VER TODOS AGENDAMENTOS
@app.route('/agendamentos', methods=['GET'])
def ver_agendamentos():
    agendamentos = Agendamento.query.all()
    return jsonify({
        "agendamentos": [a.to_dict() for a in agendamentos]
    }), 200


# 🔥 VER UM AGENDAMENTO
@app.route('/agendamentos/<int:agendamento_id>', methods=['GET'])
def ver_agendamento_especifico(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    return jsonify({
        "agendamento": agendamento.to_dict()
    }), 200


# 🔥 CRIAR AGENDAMENTO
@app.route('/criar-agendamento', methods=['POST'])
def criar_agendar():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Nenhum dado enviado"}), 400

    titulo = data.get('titulo')
    descricao = data.get('descricao')
    status = data.get('status', 0)
    agendamento_user = data.get('agendamento_user')

    if not titulo:
        return jsonify({"message": "Título é obrigatório"}), 400

    novo_agendamento = Agendamento(
        titulo=titulo,
        descricao=descricao,
        status=status,
        agendamento_user=agendamento_user
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
    agendamento = Agendamento.query.get(agendamento_id)

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Nenhum dado enviado"}), 400

    agendamento.titulo = data.get('titulo', agendamento.titulo)
    agendamento.descricao = data.get('descricao', agendamento.descricao)
    agendamento.status = data.get('status', agendamento.status)
    agendamento.agendamento_user = data.get('agendamento_user', agendamento.agendamento_user)

    db.session.commit()

    return jsonify({"message": "Atualizado com sucesso"}), 200


# 🔥 DELETAR AGENDAMENTO
@app.route('/agendamentos/<int:agendamento_id>', methods=['DELETE'])
def remover_agendamento(agendamento_id):
    agendamento = Agendamento.query.get(agendamento_id)

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