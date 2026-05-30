import os
import sqlite3

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_db():
	db_path = os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)
	conn = sqlite3.connect(db_path)
	conn.row_factory = sqlite3.Row
	conn.execute("PRAGMA foreign_keys = ON")
	return conn


def init_db():
	with get_db() as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS usuarios (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				nome TEXT NOT NULL UNIQUE,
				senha TEXT NOT NULL
			)
			"""
		)
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS agendamentos (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				agendamento_user INTEGER,
				titulo TEXT NOT NULL,
				descricao TEXT,
				status INTEGER DEFAULT 0,
				FOREIGN KEY (agendamento_user) REFERENCES usuarios(id)
			)
			"""
		)
		conn.commit()