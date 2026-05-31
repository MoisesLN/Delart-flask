import importlib
import os
import sqlite3
import sys
from pathlib import Path

import pytest


def load_app(db_path):
    os.environ["DATABASE_PATH"] = str(db_path)
    project_root = Path(__file__).resolve().parents[1]
    app_dir = project_root / "app"

    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))

    for module_name in ("app", "db"):
        if module_name in sys.modules:
            del sys.modules[module_name]

    app_module = importlib.import_module("app")
    app_module.init_db()
    app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    return app_module


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test.db"
    app_module = load_app(db_path)

    with app_module.app.test_client() as client:
        yield client, db_path


def register_user(client, nome="alice", senha="123"):
    return client.post(
        "/",
        data={"nome": nome, "senha": senha},
        follow_redirects=False,
    )


def login_user(client, nome="alice", senha="123"):
    return client.post(
        "/login",
        data={"nome": nome, "senha": senha},
        follow_redirects=False,
    )


def test_home_loads(client):
    client, _ = client
    response = client.get("/")
    assert response.status_code == 200


def test_cadastro_get(client):
    client, _ = client
    response = client.get("/")
    assert response.status_code == 200


def test_cadastro_post_success(client):
    client, _ = client
    response = register_user(client)
    assert response.status_code == 302
    assert "/dashboard" in response.headers.get("Location", "")


def test_cadastro_post_invalid(client):
    client, _ = client
    response = client.post("/", data={"nome": "", "senha": ""})
    assert response.status_code == 200
    assert b"Nome e senha" in response.data


def test_login_get(client):
    client, _ = client
    response = client.get("/login")
    assert response.status_code == 200


def test_login_success(client):
    client, _ = client
    register_user(client)
    client.get("/logout")
    response = login_user(client)
    assert response.status_code == 302
    assert "/dashboard" in response.headers.get("Location", "")


def test_login_wrong_password(client):
    client, _ = client
    register_user(client)
    client.get("/logout")
    response = login_user(client, senha="errada")
    assert response.status_code == 200
    assert "Usuário ou senha inválidos" in response.data.decode("utf-8")


def test_logout_clears_session(client):
    client, _ = client
    register_user(client)
    response = client.get("/logout")
    assert response.status_code == 302
    assert "/login" in response.headers.get("Location", "")
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert "/login" in response.headers.get("Location", "")


def test_protected_redirects_to_login(client):
    client, _ = client
    response = client.get("/agendamentos")
    assert response.status_code == 302
    assert "/login" in response.headers.get("Location", "")


def test_agendamentos_crud_flow(client):
    client, db_path = client
    register_user(client)

    response = client.get("/agendamentos")
    assert response.status_code == 200

    response = client.post(
        "/agendamentos/novo",
        data={"titulo": "Lavagem", "descricao": "Completa", "status": "1"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    response = client.get("/agendamentos")
    assert response.status_code == 200
    assert b"Lavagem" in response.data

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        agendamento = conn.execute(
            "SELECT id FROM agendamentos WHERE titulo = ?",
            ("Lavagem",),
        ).fetchone()

    assert agendamento is not None
    agendamento_id = agendamento["id"]

    response = client.get(f"/agendamentos/{agendamento_id}")
    assert response.status_code == 200

    response = client.post(
        f"/agendamentos/{agendamento_id}/editar",
        data={"titulo": "Lavagem Premium", "descricao": "Completa", "status": "2"},
        follow_redirects=False,
    )
    assert response.status_code == 302

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        agendamento = conn.execute(
            "SELECT titulo, status FROM agendamentos WHERE id = ?",
            (agendamento_id,),
        ).fetchone()

    assert agendamento["titulo"] == "Lavagem Premium"
    assert agendamento["status"] == 2

    response = client.post(
        f"/agendamentos/{agendamento_id}/remover",
        follow_redirects=False,
    )
    assert response.status_code == 302

    with sqlite3.connect(db_path) as conn:
        agendamento = conn.execute(
            "SELECT id FROM agendamentos WHERE id = ?",
            (agendamento_id,),
        ).fetchone()

    assert agendamento is None


def test_agendamentos_query_filters(client):
    client, _ = client
    register_user(client)

    client.post(
        "/agendamentos/novo",
        data={"titulo": "Corte", "descricao": "Simples", "status": "0"},
        follow_redirects=False,
    )
    client.post(
        "/agendamentos/novo",
        data={"titulo": "Corte Especial", "descricao": "Premium", "status": "1"},
        follow_redirects=False,
    )

    response = client.get("/agendamentos?busca=corte")
    assert response.status_code == 200

    response = client.get("/agendamentos?status=0")
    assert response.status_code == 200
    assert b"Corte" in response.data

    response = client.get("/agendamentos?status=1")
    assert response.status_code == 200
    assert b"Corte Especial" in response.data

    response = client.get("/agendamentos?busca=corte&status=1")
    assert response.status_code == 200
    assert b"Corte Especial" in response.data
