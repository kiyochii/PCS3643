"""Modelo da Aula 2, com armazenamento SQLite e operações de edição, remoção e consulta."""

from database import conectar


class Filme:

    def __init__(self, codigo = None, nome=None, data_estreia=None, data_saida=None, duracao=None):
        self.codigo = codigo
        self.nome = nome
        self.data_estreia = data_estreia
        self.data_saida = data_saida
        self.duracao = duracao


class Sala:

    def __init__(self, numero=None, capacidade=None, tipo=None):
        self.numero = numero
        self.capacidade = capacidade
        self.tipo = tipo


class Sessao:
    def __init__(self, sala=None, filme=None, data=None, hora_inicio=None):
#        self.codigo
        self.sala = sala
        self.filme = filme
        self.data = data
        self.hora_inicio = hora_inicio


class TipoIngresso:
    def __init__(self, codigo, nome, percentual):
        self.codigo = codigo
        self.nome = nome
        self.percentual = percentual


class NaoEncontrado(ValueError):
    pass


class Conflito(ValueError):
    pass


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


def cadastrar_filme(nome, data_estreia, data_saida, duracao):
    with conectar(escrita=True) as conexao:
        cursor = conexao.execute(
            "INSERT INTO filmes (nome, data_estreia, data_saida, duracao) VALUES (?, ?, ?, ?)",
            (nome, data_estreia, data_saida, duracao),
        )
        filme = Filme(cursor.lastrowid, nome, data_estreia, data_saida, duracao)
        return filme


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


# Operações acrescentadas na Aula 3.


def _buscar(conexao, tabela, chave, valor):
    # Tabela e chave vêm somente das chamadas fixas deste módulo.
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
