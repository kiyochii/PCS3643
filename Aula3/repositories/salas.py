"""Persistência e operações de salas."""

from database import conectar
from models import Conflito, Sala
from .base import _buscar, _remover


def cadastrar_sala(numero, capacidade, tipo_sala):
    if not isinstance(numero, int) or isinstance(numero, bool) or numero <= 0:
        return None

    if not isinstance(capacidade, int) or isinstance(capacidade, bool) or capacidade <= 0:
        return None

    if tipo_sala not in ("2D", "3D"):
        return None

    with conectar(escrita=True) as conexao:
        if conexao.execute("SELECT 1 FROM salas WHERE numero = ?", (numero,)).fetchone():
            return None

        sala = Sala(numero, capacidade, tipo_sala)
        conexao.execute("INSERT INTO salas VALUES (?, ?, ?)", (numero, capacidade, tipo_sala))
        return sala


def listar_salas():
    with conectar() as conexao:
        return [Sala(**dict(linha)) for linha in conexao.execute("SELECT * FROM salas ORDER BY numero")]


def editar_sala(numero, capacidade, tipo_sala):
    with conectar(escrita=True) as conexao:
        atual = _buscar(conexao, "salas", "numero", numero)
        tem_sessoes = conexao.execute("SELECT 1 FROM sessoes WHERE numero_sala = ? LIMIT 1", (numero,)).fetchone()
        if tem_sessoes and (atual["capacidade"] != capacidade or atual["tipo"] != tipo_sala):
            raise Conflito("Remova as sessões da sala antes de alterar sua capacidade ou tipo.")
        conexao.execute("UPDATE salas SET capacidade = ?, tipo = ? WHERE numero = ?", (capacidade, tipo_sala, numero))
        return Sala(numero, capacidade, tipo_sala)


def remover_sala(numero):
    _remover("salas", "numero", numero)
