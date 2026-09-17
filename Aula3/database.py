"""Criação e conexão com o banco SQLite do cinema."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().with_name("cinema.db")


@contextmanager
def conectar(escrita=False):
    conexao = sqlite3.connect(DB_PATH, timeout=10)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    try:
        # Mantém cada alteração em uma única transação.
        if escrita:
            conexao.execute("BEGIN IMMEDIATE")
        with conexao:
            yield conexao
    finally:
        conexao.close()


def criar_tabelas():
    with conectar() as conexao:
        conexao.executescript("""
            CREATE TABLE IF NOT EXISTS filmes (
                codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_estreia TEXT NOT NULL,
                data_saida TEXT NOT NULL,
                duracao INTEGER NOT NULL CHECK (duracao > 0)
            );
            CREATE TABLE IF NOT EXISTS precos (
                tipo_sala TEXT PRIMARY KEY CHECK (tipo_sala IN ('2D', '3D')),
                valor_ingresso INTEGER NOT NULL CHECK (valor_ingresso > 0)
            );
            CREATE TABLE IF NOT EXISTS salas (
                numero INTEGER PRIMARY KEY CHECK (numero > 0),
                capacidade INTEGER NOT NULL CHECK (capacidade > 0),
                tipo TEXT NOT NULL CHECK (tipo IN ('2D', '3D'))
            );
            CREATE TABLE IF NOT EXISTS tipos_ingresso (
                codigo INTEGER PRIMARY KEY CHECK (codigo >= 0),
                nome TEXT NOT NULL,
                percentual INTEGER NOT NULL CHECK (percentual BETWEEN 1 AND 100)
            );
            CREATE TABLE IF NOT EXISTS sessoes (
                codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_sala INTEGER NOT NULL REFERENCES salas(numero),
                codigo_filme INTEGER NOT NULL REFERENCES filmes(codigo),
                data_sessao TEXT NOT NULL,
                hora_inicio INTEGER NOT NULL CHECK (hora_inicio BETWEEN 0 AND 23),
                UNIQUE (numero_sala, data_sessao, hora_inicio)
            );
            CREATE TABLE IF NOT EXISTS assentos (
                codigo_sessao INTEGER NOT NULL REFERENCES sessoes(codigo) ON DELETE CASCADE,
                numero INTEGER NOT NULL CHECK (numero > 0),
                ocupado INTEGER NOT NULL DEFAULT 0 CHECK (ocupado IN (0, 1)),
                PRIMARY KEY (codigo_sessao, numero)
            );
        """)
