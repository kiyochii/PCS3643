from datetime import datetime

filmes = []
salas = []
sessoes = []
tipo_sala = {}


class Filme:

    def __init__(self, codigo=None, nome=None, data_estreia=None, data_saida=None, duracao=None):
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
        self.sala = sala
        self.filme = filme
        self.data = data
        self.hora_inicio = hora_inicio


def _parse_data(data):
    if not isinstance(data, str):
        return None
    try:
        return datetime.strptime(data, "%d/%m/%Y")
    except (TypeError, ValueError):
        return None


def _data_valida(data):
    return _parse_data(data) is not None


def pegar_sala(numero):
    for sala in salas:
        if sala.numero == numero:
            return sala
    return None


def pegar_filme(codigo):
    for filme in filmes:
        if filme.codigo == codigo:
            return filme
    return None


def pegar_sessao(codigo):
    for sessao in sessoes:
        if sessao.codigo == codigo:
            return sessao
    return None


def cadastrar_valor_ingresso(tipo_sala_input, valor_ingresso):
    if isinstance(tipo_sala_input, dict):
        tipo = tipo_sala_input.get("tipo")
    else:
        tipo = tipo_sala_input

    if not isinstance(tipo, str):
        return False

    tipo = tipo.strip()
    if tipo not in ("2D", "3D"):
        return False

    if not isinstance(valor_ingresso, int) or isinstance(valor_ingresso, bool):
        return False

    if valor_ingresso <= 0:
        return False

    tipo_sala[tipo] = valor_ingresso
    return True


def cadastrar_sala(numero, capacidade, tipo_sala_param):
    if not isinstance(numero, int) or isinstance(numero, bool) or numero <= 0:
        return None

    if not isinstance(capacidade, int) or isinstance(capacidade, bool) or capacidade <= 0:
        return None

    if not isinstance(tipo_sala_param, str) or tipo_sala_param not in ("2D", "3D"):
        return None

    if any(sala.numero == numero for sala in salas):
        return None

    sala = Sala(numero, capacidade, tipo_sala_param)
    salas.append(sala)
    return sala


def cadastrar_filme(nome, data_estreia, data_saida, duracao):
    if not isinstance(nome, str) or not nome.strip():
        return None

    if not _data_valida(data_estreia) or not _data_valida(data_saida):
        return None

    if not isinstance(duracao, int) or isinstance(duracao, bool) or duracao <= 0:
        return None

    data_inicio = _parse_data(data_estreia)
    data_fim = _parse_data(data_saida)
    if data_inicio > data_fim:
        return None

    nome_limpo = nome.strip()
    if any(filme.nome.lower() == nome_limpo.lower() for filme in filmes):
        return None

    codigo = len(filmes) + 1
    filme = Filme(codigo, nome_limpo, data_estreia, data_saida, duracao)
    filmes.append(filme)
    return filme


def cadastrar_sessao(numero_sala, codigo_filme, data_sessao, hora_inicio):
    if not isinstance(numero_sala, int) or isinstance(numero_sala, bool):
        return None
    if not isinstance(codigo_filme, int) or isinstance(codigo_filme, bool):
        return None
    if not isinstance(hora_inicio, int) or isinstance(hora_inicio, bool):
        return None
    if not isinstance(data_sessao, str) or not _data_valida(data_sessao):
        return None
    if hora_inicio < 0 or hora_inicio > 23:
        return None

    sala_encontrada = pegar_sala(numero_sala)
    if sala_encontrada is None:
        return None

    filme_encontrado = pegar_filme(codigo_filme)
    if filme_encontrado is None:
        return None

    for sessao in sessoes:
        if (
            sessao.sala.numero == numero_sala
            and sessao.data == data_sessao
            and sessao.hora_inicio == hora_inicio
        ):
            return None

    nova_sessao = Sessao(sala_encontrada, filme_encontrado, data_sessao, hora_inicio)
    nova_sessao.codigo = len(sessoes) + 1
    nova_sessao.assentos = {numero: 0 for numero in range(1, sala_encontrada.capacidade + 1)}
    sessoes.append(nova_sessao)
    return nova_sessao


def listar_filmes_por_data(data):
    if not _data_valida(data):
        return "Data invalida."

    linhas = []
    for sessao in sorted(sessoes, key=lambda item: item.codigo):
        if sessao.data != data:
            continue
        if not any(assento == 0 for assento in sessao.assentos.values()):
            continue
        valor = tipo_sala.get(sessao.sala.tipo)
        if valor is None:
            continue
        linhas.append(
            f"{sessao.codigo}: {sessao.filme.nome}, sala {sessao.sala.numero} ({sessao.sala.tipo}), {sessao.hora_inicio}h, {valor} reais."
        )

    if not linhas:
        return "Nenhum filme no dia escolhido."
    return "\n".join(linhas)


def comprarIngressos(codigo_sessao, assentos, tipos_ingresso):
    sessao = pegar_sessao(codigo_sessao)
    if sessao is None:
        return 0

    if not isinstance(assentos, list) or not isinstance(tipos_ingresso, list):
        return 0

    if not assentos or not tipos_ingresso:
        return 0

    if len(assentos) != len(tipos_ingresso):
        return 0

    if len(set(assentos)) != len(assentos):
        return 0

    for assento in assentos:
        if not isinstance(assento, int) or isinstance(assento, bool):
            return 0
        if assento <= 0 or assento > sessao.sala.capacidade:
            return 0
        if sessao.assentos.get(assento, 0) != 0:
            return 0

    for tipo in tipos_ingresso:
        if not isinstance(tipo, int) or isinstance(tipo, bool):
            return 0
        if tipo not in (0, 1):
            return 0

    valor_unitario = tipo_sala.get(sessao.sala.tipo)
    if valor_unitario is None or valor_unitario <= 0:
        return 0

    total = 0
    for assento, tipo in zip(assentos, tipos_ingresso):
        if tipo == 0:
            total += valor_unitario
        else:
            total += valor_unitario / 2

    for assento in assentos:
        sessao.assentos[assento] = 1

    return total
