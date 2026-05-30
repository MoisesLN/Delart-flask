from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, init_db

app = Flask(__name__)
app.secret_key = 'd626428838bab4dd0736eb2e79918e0e'


def row_to_dict(row):
    return dict(row) if row else None


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

        with get_db() as conn:
            usuario_existente = conn.execute(
                "SELECT id FROM usuarios WHERE nome = ?",
                (nome,)
            ).fetchone()

        if usuario_existente:
            return render_template(
                'cadastro.html',
                erro='Este nome de usuário já está em uso'
            )

        senha_hash = generate_password_hash(senha)
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO usuarios (nome, senha) VALUES (?, ?)",
                (nome, senha_hash)
            )
            conn.commit()
            novo_id = cursor.lastrowid

            novo_usuario = conn.execute(
                "SELECT id, nome FROM usuarios WHERE id = ?",
                (novo_id,)
            ).fetchone()

        session['usuario_id'] = novo_usuario['id']
        session['usuario_nome'] = novo_usuario['nome']

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

        with get_db() as conn:
            usuario = conn.execute(
                "SELECT id, nome, senha FROM usuarios WHERE nome = ?",
                (nome,)
            ).fetchone()

        senha_armazenada = usuario['senha'] if usuario else ''
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

        session['usuario_id'] = usuario['id']
        session['usuario_nome'] = usuario['nome']

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

    with get_db() as conn:
        agendamentos = conn.execute(
            """
            SELECT id, agendamento_user, titulo, descricao, status
            FROM agendamentos
            WHERE agendamento_user = ?
            """,
            (session['usuario_id'],)
        ).fetchall()

    return jsonify({
        "agendamentos": [row_to_dict(a) for a in agendamentos]
    }), 200


# 🔥 VER UM AGENDAMENTO
@app.route('/agendamentos/<int:agendamento_id>', methods=['GET'])
def ver_agendamento_especifico(agendamento_id):
    if 'usuario_id' not in session:
        return jsonify({"message": "Não autenticado"}), 401

    with get_db() as conn:
        agendamento = conn.execute(
            """
            SELECT id, agendamento_user, titulo, descricao, status
            FROM agendamentos
            WHERE id = ? AND agendamento_user = ?
            """,
            (agendamento_id, session['usuario_id'])
        ).fetchone()

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    return jsonify({
        "agendamento": row_to_dict(agendamento)
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

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO agendamentos (agendamento_user, titulo, descricao, status)
            VALUES (?, ?, ?, ?)
            """,
            (session['usuario_id'], titulo, descricao, status)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        novo_agendamento = conn.execute(
            """
            SELECT id, agendamento_user, titulo, descricao, status
            FROM agendamentos
            WHERE id = ? AND agendamento_user = ?
            """,
            (novo_id, session['usuario_id'])
        ).fetchone()

    return jsonify({
        "message": "Criado com sucesso",
        "agendamento": row_to_dict(novo_agendamento)
    }), 201


# 🔥 ATUALIZAR AGENDAMENTO
@app.route('/agendamentos/<int:agendamento_id>', methods=['PUT'])
def atualizar_agendamento(agendamento_id):
    if 'usuario_id' not in session:
        return jsonify({"message": "Não autenticado"}), 401

    with get_db() as conn:
        agendamento = conn.execute(
            """
            SELECT id, agendamento_user, titulo, descricao, status
            FROM agendamentos
            WHERE id = ? AND agendamento_user = ?
            """,
            (agendamento_id, session['usuario_id'])
        ).fetchone()

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"message": "Nenhum dado enviado"}), 400

    titulo = data.get('titulo', agendamento['titulo'])
    descricao = data.get('descricao', agendamento['descricao'])
    status = data.get('status', agendamento['status'])

    with get_db() as conn:
        conn.execute(
            """
            UPDATE agendamentos
            SET titulo = ?, descricao = ?, status = ?
            WHERE id = ? AND agendamento_user = ?
            """,
            (titulo, descricao, status, agendamento_id, session['usuario_id'])
        )
        conn.commit()

    return jsonify({"message": "Atualizado com sucesso"}), 200


# 🔥 DELETAR AGENDAMENTO
@app.route('/agendamentos/<int:agendamento_id>', methods=['DELETE'])
def remover_agendamento(agendamento_id):
    if 'usuario_id' not in session:
        return jsonify({"message": "Não autenticado"}), 401

    with get_db() as conn:
        agendamento = conn.execute(
            """
            SELECT id FROM agendamentos
            WHERE id = ? AND agendamento_user = ?
            """,
            (agendamento_id, session['usuario_id'])
        ).fetchone()

    if not agendamento:
        return jsonify({"message": "Agendamento não encontrado"}), 404

    with get_db() as conn:
        conn.execute(
            "DELETE FROM agendamentos WHERE id = ? AND agendamento_user = ?",
            (agendamento_id, session['usuario_id'])
        )
        conn.commit()

    return jsonify({"message": "Deletado com sucesso"}), 200


# 🔥 START APP
if __name__ == '__main__':
    init_db()

    app.run(debug=True)