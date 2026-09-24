"""Persistência e operações de filmes."""

from database import conectar
from models import Filme
from .base import _buscar, _remover


def cadastrar_filme(nome, data_estreia, data_saida, duracao):
    with conectar(escrita=True) as conexao:
        cursor = conexao.execute(
            "INSERT INTO filmes (nome, data_estreia, data_saida, duracao) VALUES (?, ?, ?, ?)",
            (nome, data_estreia, data_saida, duracao),
        )
        filme = Filme(cursor.lastrowid, nome, data_estreia, data_saida, duracao)
        return filme


def listar_filmes():
    with conectar() as conexao:
        return [Filme(**dict(linha)) for linha in conexao.execute("SELECT * FROM filmes ORDER BY codigo")]


def editar_filme(codigo, nome, data_estreia, data_saida, duracao):
    with conectar(escrita=True) as conexao:
        _buscar(conexao, "filmes", "codigo", codigo)
        conexao.execute(
            "UPDATE filmes SET nome = ?, data_estreia = ?, data_saida = ?, duracao = ? WHERE codigo = ?",
            (nome, data_estreia, data_saida, duracao, codigo),
        )
        return Filme(codigo, nome, data_estreia, data_saida, duracao)


def remover_filme(codigo):
    _remover("filmes", "codigo", codigo)
