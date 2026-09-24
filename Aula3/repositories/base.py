"""Operações SQLite compartilhadas pelos repositórios."""

from database import conectar
from models import NaoEncontrado


def _buscar(conexao, tabela, chave, valor):
    # Tabela e chave vêm somente das chamadas fixas dos repositórios.
    linha = conexao.execute(
        f"SELECT * FROM {tabela} WHERE {chave} = ?", (valor,)
    ).fetchone()
    if linha is None:
        raise NaoEncontrado(f"Registro não encontrado em {tabela}.")
    return linha


def _remover(tabela, chave, valor):
    with conectar(escrita=True) as conexao:
        _buscar(conexao, tabela, chave, valor)
        conexao.execute(f"DELETE FROM {tabela} WHERE {chave} = ?", (valor,))
