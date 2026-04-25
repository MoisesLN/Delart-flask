from flask import Flask, jsonify, request, render_template
from db import db
from models import Usuario, Agendamento

app = Flask(__name__)
app.secret_key = 'd626428838bab4dd0736eb2e79918e0e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app) # conecta o objeto db ao aplicativo flask


@app.route('/')
def cadastro():
    return render_template('cadastro.html')


#Função de Read (um endpoint pra ver todos, outro pra ver especifico)
@app.route('/agendamentos', methods=['GET'])
def ver_agendamentos():
    agendamentos = Agendamento.query.all()

    return jsonify({"agendamentos": [agendamento.to_dict() for agendamento in agendamentos]}), 200 # jsonify -> trasformar dados do python em uam resposta json

@app.route('/agendamentos/<int:agendamento_id>', methods=['GET'])
def ver_agendamento_especifico():
    agendamento = Agendameto.query.get(agendamento_id)

    if not agendamento:
        jsonify({"mensage": "Agendamento não encontrado"}), 404

    return jsonify({"agendamento": agendameto.to_dict}), 200


#Função Criar
@app.route('/criar-agendamento', methods=['POST'])
def criar_agendar():
    data = request.get_json()

    if not data:
        return jsonify({"mensage": "Nenhum dado foi enviado"}), 400

    titulo = data.get('titulo')
    descricao = data.get('descricao')
    status = data.get('status', 0)
    agendamento_user = data.get('agendamento_user')

    if not titulo:
        return jsonify({"mensage": "O titulo é obrigatório"}), 400

    # cria um novo registro de agendamento e salva no banco de dados
    novo_agendamento = Agendamento( #cria um objeto do model
        titulo=titulo,
        descricao=descricao,
        status=status,
        agendamento_user=agendamento_user
    )

    db.session.add(novo_agendamento) # adiciona na sessão
    db.session.commit() # envia a operação para o banco

    return jsonify({"message": "Agendamento criado com sucesso","agendamento": novo_agendamento.to_dict()}), 201

#Função de Atualizar
@app.route('/agendamentos/<int:agendamento_id>',methods=['PUT'])
def atualizar_agendamento():
    agendamento = Agendamento.query.get(agendamento_id)

    if not agendamento:
        return jsonify({"mensage": "Agendamento não encontrado"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"mensage": "Nenhum dado foi enviado"}), 400

    # altera apenas os campos que vierem no JSON da requisição e mantém os valores antigos nos campos que não vierem
    agendamento.titulo = data.get('titulo', agendamento.titulo)
    agendamento.descricao = data.get('descricao', agendamento.descricao)
    agendamento.status = data.get('status', agendamento.status)
    agendamento.agendamento_user = data.get('agendamento_user', agendamento.agendamento_user)

    db.session.commit() #obs.: Não necessario usar o session.add porque o o resgistro ja existe na sessão, então e so mandar as mudanças

@app.route('/agendamentos/<int:agendamento_id>',methods=['DELETE'])
def remover_agendamento():
    agendamento = Agendamento.query.get(agendamento_id)

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    db.session.delete(agendamento)
    db.session.commit()

    return jsonify({"message": "Agendamento deletado com sucesso"}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # cria as tabelas
    app.run(debug=True)