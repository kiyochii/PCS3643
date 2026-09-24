"""Persistência e operações de tipos ingresso."""

from database import conectar
from models import TipoIngresso
from .base import _buscar, _remover


def listar_tipos_ingresso():
    with conectar() as conexao:
        return [TipoIngresso(**dict(linha)) for linha in conexao.execute("SELECT * FROM tipos_ingresso ORDER BY codigo")]


def cadastrar_tipo_ingresso(codigo, nome, percentual):
    with conectar(escrita=True) as conexao:
        conexao.execute("INSERT INTO tipos_ingresso VALUES (?, ?, ?)", (codigo, nome, percentual))
        return TipoIngresso(codigo, nome, percentual)


def editar_tipo_ingresso(codigo, nome, percentual):
    with conectar(escrita=True) as conexao:
        _buscar(conexao, "tipos_ingresso", "codigo", codigo)
        conexao.execute("UPDATE tipos_ingresso SET nome = ?, percentual = ? WHERE codigo = ?", (nome, percentual, codigo))
        return TipoIngresso(codigo, nome, percentual)


def remover_tipo_ingresso(codigo):
    _remover("tipos_ingresso", "codigo", codigo)
