"""Persistência e operações de precos."""

from database import conectar
from .base import _buscar, _remover


def cadastrar_valor_ingresso(tipo_sala_param, valor_ingresso):
    if not isinstance(tipo_sala_param, dict):
        return False

    tipo = tipo_sala_param.get("tipo")
    if not isinstance(tipo, str):
        return False

    if tipo not in ("2D", "3D"):
        return False

    if not isinstance(valor_ingresso, int) or isinstance(valor_ingresso, bool):
        return False

    if valor_ingresso <= 0:
        return False

    with conectar(escrita=True) as conexao:
        conexao.execute(
            "INSERT INTO precos VALUES (?, ?) ON CONFLICT(tipo_sala) "
            "DO UPDATE SET valor_ingresso = excluded.valor_ingresso",
            (tipo, valor_ingresso),
        )
    return True


def listar_precos():
    with conectar() as conexao:
        return [dict(linha) for linha in conexao.execute("SELECT * FROM precos ORDER BY tipo_sala")]


def editar_valor_ingresso(tipo_sala, valor_ingresso):
    with conectar(escrita=True) as conexao:
        _buscar(conexao, "precos", "tipo_sala", tipo_sala)
        conexao.execute("UPDATE precos SET valor_ingresso = ? WHERE tipo_sala = ?", (valor_ingresso, tipo_sala))
        return {"tipo_sala": tipo_sala, "valor_ingresso": valor_ingresso}


def remover_valor_ingresso(tipo_sala):
    _remover("precos", "tipo_sala", tipo_sala)
