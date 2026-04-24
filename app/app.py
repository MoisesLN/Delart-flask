from flask import Flask, jsonify, request
from db import db, Usuario, Agendamento

app = Flask(__name__)
app.secret_key = 'd626428838bab4dd0736eb2e79918e0e'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# db.init_app(app)


@app.route('/')
def cadastro():
    return render_template('cadastro.html')

#Função de Read (um endpoint pra ver todos, outro pra ver especifico)
@app.route('/agendamentos', methods=['GET'])
def ver_agendamentos():
    ...

@app.route('/agendamentos/<int:agendamento_id>', methods=['GET'])
def ver_agendamento_especifico():
    ...

#Função Update
@app.route('/criar-agendamento', methods=['POST'])
def criar_agendar():
    data = request.get_json()
    novo_agendamento = {
        "id": Agendamento.id,
        "titulo": data.get('titulo'),
        "descricao": data.get('descricao'),
        "status": data.get('status')
    }

    return jsonify({"mensage": "Agendamento criado com sucesso", "agendamento": novo_agendamento}), 201

if __name__ == '__main__':
    app.run(debug=True)