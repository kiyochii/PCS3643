"""Persistência e operações de sessoes."""

from database import conectar
from models import Filme, Sala, Sessao
from .base import _buscar, _remover


def cadastrar_sessao(numero_sala, codigo_filme, data_sessao, hora_inicio):
    # 1. Verificar os tipos dos parâmetros
    if (
        type(numero_sala) is not int
        or type(codigo_filme) is not int
        or type(hora_inicio) is not int
        or not isinstance(data_sessao, str)
    ):
        return None

    # 2. Verificar se a hora de início está entre 0 e 23
    if hora_inicio < 0 or hora_inicio > 23:
        return None

    with conectar(escrita=True) as conexao:
        # 3. Buscar a sala pelo número, agora no banco.
        linha = conexao.execute("SELECT * FROM salas WHERE numero = ?", (numero_sala,)).fetchone()
        if linha is None:
            return None
        sala_encontrada = Sala(**dict(linha))

        # 4. Buscar o filme pelo código.
        linha = conexao.execute("SELECT * FROM filmes WHERE codigo = ?", (codigo_filme,)).fetchone()
        if linha is None:
            return None
        filme_encontrado = Filme(**dict(linha))

        # 5. Verificar se já existe uma sessão na mesma sala, data e hora de início.
        if conexao.execute(
            "SELECT 1 FROM sessoes WHERE numero_sala = ? AND data_sessao = ? AND hora_inicio = ?",
            (numero_sala, data_sessao, hora_inicio),
        ).fetchone():
            return None

        # 6. Criar o objeto da sessão.
        nova_sessao = Sessao(sala_encontrada, filme_encontrado, data_sessao, hora_inicio)

        # 7. O banco gera o código sequencial para a sessão.
        cursor = conexao.execute(
            "INSERT INTO sessoes (numero_sala, codigo_filme, data_sessao, hora_inicio) VALUES (?, ?, ?, ?)",
            (numero_sala, codigo_filme, data_sessao, hora_inicio),
        )
        nova_sessao.codigo = cursor.lastrowid

        # 8. Numerar os assentos de 1 até a capacidade da sala e inicializá-los com 0.
        nova_sessao.assentos = {}
        for numero in range(1, sala_encontrada.capacidade + 1):
            nova_sessao.assentos[numero] = 0

        # 9. Salvar os assentos e retornar o objeto criado.
        conexao.executemany(
            "INSERT INTO assentos (codigo_sessao, numero, ocupado) VALUES (?, ?, ?)",
            ((nova_sessao.codigo, numero, ocupado) for numero, ocupado in nova_sessao.assentos.items()),
        )
        return nova_sessao


def _sessao(conexao, linha):
    sala = Sala(**dict(_buscar(conexao, "salas", "numero", linha["numero_sala"])))
    filme = Filme(**dict(_buscar(conexao, "filmes", "codigo", linha["codigo_filme"])))
    assentos = {
        assento["numero"]: assento["ocupado"]
        for assento in conexao.execute(
            "SELECT numero, ocupado FROM assentos WHERE codigo_sessao = ? ORDER BY numero", (linha["codigo"],)
        )
    }
    sessao = Sessao(sala, filme, linha["data_sessao"], linha["hora_inicio"])
    sessao.codigo = linha["codigo"]
    sessao.assentos = assentos
    return sessao


def _criar_assentos(conexao, codigo, capacidade):
    conexao.executemany(
        "INSERT INTO assentos (codigo_sessao, numero) VALUES (?, ?)",
        ((codigo, numero) for numero in range(1, capacidade + 1)),
    )


def listar_sessoes():
    with conectar() as conexao:
        linhas = conexao.execute("SELECT * FROM sessoes ORDER BY codigo").fetchall()
        return [_sessao(conexao, linha) for linha in linhas]


def editar_sessao(codigo, numero_sala, codigo_filme, data_sessao, hora_inicio):
    with conectar(escrita=True) as conexao:
        _buscar(conexao, "sessoes", "codigo", codigo)
        sala = _buscar(conexao, "salas", "numero", numero_sala)
        _buscar(conexao, "filmes", "codigo", codigo_filme)
        conexao.execute(
            "UPDATE sessoes SET numero_sala = ?, codigo_filme = ?, data_sessao = ?, hora_inicio = ? WHERE codigo = ?",
            (numero_sala, codigo_filme, data_sessao, hora_inicio, codigo),
        )
        conexao.execute("DELETE FROM assentos WHERE codigo_sessao = ?", (codigo,))
        _criar_assentos(conexao, codigo, sala["capacidade"])
        return _sessao(conexao, _buscar(conexao, "sessoes", "codigo", codigo))


def remover_sessao(codigo):
    _remover("sessoes", "codigo", codigo)
