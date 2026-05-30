from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_db, init_db

app = Flask(__name__)
app.secret_key = 'd626428838bab4dd0736eb2e79918e0e'


def row_to_dict(row):
    return dict(row) if row else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)

    return wrapped


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


# 🔥 LISTAR AGENDAMENTOS (HTML)
@app.route('/agendamentos', methods=['GET'])
@login_required
def listar_agendamentos():
    busca = request.args.get('busca', '').strip()
    status = request.args.get('status', '').strip()

    query = """
        SELECT id, agendamento_user, titulo, descricao, status
        FROM agendamentos
        WHERE agendamento_user = ?
    """
    params = [session['usuario_id']]

    if busca:
        query += " AND (titulo LIKE ? OR descricao LIKE ?)"
        like = f"%{busca}%"
        params.extend([like, like])

    status_filtrado = status
    if status != '':
        try:
            status_int = int(status)
            query += " AND status = ?"
            params.append(status_int)
        except ValueError:
            status_filtrado = ''

    query += " ORDER BY id DESC"

    with get_db() as conn:
        agendamentos = conn.execute(query, params).fetchall()

    return render_template(
        'agendamentos/listar.html',
        agendamentos=agendamentos,
        busca=busca,
        status=status_filtrado
    )


# 🔥 NOVO AGENDAMENTO (HTML)
@app.route('/agendamentos/novo', methods=['GET', 'POST'])
@login_required
def novo_agendamento():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        status = request.form.get('status', '0').strip()

        if not titulo:
            flash('Título é obrigatório', 'error')
            return redirect(url_for('novo_agendamento'))

        try:
            status_int = int(status)
        except ValueError:
            status_int = 0

        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO agendamentos (agendamento_user, titulo, descricao, status)
                VALUES (?, ?, ?, ?)
                """,
                (session['usuario_id'], titulo, descricao, status_int)
            )
            conn.commit()

        flash('Agendamento cadastrado com sucesso', 'success')
        return redirect(url_for('listar_agendamentos'))

    return render_template('agendamentos/novo.html')


# 🔥 DETALHE DO AGENDAMENTO (HTML)
@app.route('/agendamentos/<int:agendamento_id>', methods=['GET'])
@login_required
def detalhe_agendamento(agendamento_id):
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
        flash('Agendamento não encontrado', 'warning')
        return redirect(url_for('listar_agendamentos'))

    return render_template('agendamentos/detalhe.html', agendamento=agendamento)


# 🔥 EDITAR AGENDAMENTO (HTML)
@app.route('/agendamentos/<int:agendamento_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_agendamento(agendamento_id):
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
        flash('Agendamento não encontrado', 'warning')
        return redirect(url_for('listar_agendamentos'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        status = request.form.get('status', '0').strip()

        if not titulo:
            flash('Título é obrigatório', 'error')
            return redirect(url_for('editar_agendamento', agendamento_id=agendamento_id))

        try:
            status_int = int(status)
        except ValueError:
            status_int = agendamento['status']

        with get_db() as conn:
            conn.execute(
                """
                UPDATE agendamentos
                SET titulo = ?, descricao = ?, status = ?
                WHERE id = ? AND agendamento_user = ?
                """,
                (titulo, descricao, status_int, agendamento_id, session['usuario_id'])
            )
            conn.commit()

        flash('Agendamento atualizado com sucesso', 'success')
        return redirect(url_for('listar_agendamentos'))

    return render_template('agendamentos/editar.html', agendamento=agendamento)


# 🔥 REMOVER AGENDAMENTO (HTML)
@app.route('/agendamentos/<int:agendamento_id>/remover', methods=['POST'])
@login_required
def remover_agendamento_html(agendamento_id):
    with get_db() as conn:
        agendamento = conn.execute(
            "SELECT id FROM agendamentos WHERE id = ? AND agendamento_user = ?",
            (agendamento_id, session['usuario_id'])
        ).fetchone()

    if not agendamento:
        flash('Agendamento não encontrado', 'warning')
        return redirect(url_for('listar_agendamentos'))

    with get_db() as conn:
        conn.execute(
            "DELETE FROM agendamentos WHERE id = ? AND agendamento_user = ?",
            (agendamento_id, session['usuario_id'])
        )
        conn.commit()

    flash('Agendamento removido com sucesso', 'success')
    return redirect(url_for('listar_agendamentos'))


# 🔥 VER TODOS AGENDAMENTOS
@app.route('/api/agendamentos', methods=['GET'])
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
@app.route('/api/agendamentos/<int:agendamento_id>', methods=['GET'])
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