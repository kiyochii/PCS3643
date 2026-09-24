from datetime import datetime

filmes = []
salas = []
sessoes = []
tipo_sala = {}


class Filme:

    def __init__(self, codigo=None, nome=None, data_estreia=None, data_saida=None, duracao=None, cartaz_url=None):
        self.codigo = codigo
        self.nome = nome
        self.data_estreia = data_estreia
        self.data_saida = data_saida
        self.duracao = duracao
        self.cartaz_url = cartaz_url


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

    for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(data, fmt)
        except (TypeError, ValueError):
            continue
    return None


def _data_valida(data):
    return _parse_data(data) is not None


def _normalizar_data(data):
    data_obj = _parse_data(data)
    if data_obj is None:
        return None
    return data_obj.strftime("%d-%m-%Y")


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


def atualizar_valor_ingresso(tipo_sala_input, valor_ingresso):
    if isinstance(tipo_sala_input, dict):
        tipo = tipo_sala_input.get("tipo")
    else:
        tipo = tipo_sala_input

    if not isinstance(tipo, str):
        return False

    tipo = tipo.strip()
    if tipo not in tipo_sala:
        return False

    if not isinstance(valor_ingresso, int) or isinstance(valor_ingresso, bool):
        return False

    if valor_ingresso <= 0:
        return False

    tipo_sala[tipo] = valor_ingresso
    return True


def remover_valor_ingresso(tipo_sala_input):
    if isinstance(tipo_sala_input, dict):
        tipo = tipo_sala_input.get("tipo")
    else:
        tipo = tipo_sala_input

    if not isinstance(tipo, str):
        return False

    tipo = tipo.strip()
    if tipo not in tipo_sala:
        return False

    del tipo_sala[tipo]
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


def cadastrar_filme(nome, data_estreia, data_saida, duracao, cartaz_url=None):
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

    data_estreia_padrao = data_inicio.strftime("%d-%m-%Y")
    data_saida_padrao = data_fim.strftime("%d-%m-%Y")

    codigo = len(filmes) + 1
    filme = Filme(codigo, nome_limpo, data_estreia_padrao, data_saida_padrao, duracao, cartaz_url)
    filmes.append(filme)
    return filme


def atualizar_filme(codigo_filme, nome=None, data_estreia=None, data_saida=None, duracao=None, cartaz_url=None):
    filme = pegar_filme(codigo_filme)
    if filme is None:
        return None

    novo_nome = filme.nome if nome is None else nome.strip() if isinstance(nome, str) else None
    if novo_nome is None or not novo_nome:
        return None

    nova_data_estreia = filme.data_estreia if data_estreia is None else data_estreia
    nova_data_saida = filme.data_saida if data_saida is None else data_saida
    nova_duracao = filme.duracao if duracao is None else duracao

    if not _data_valida(nova_data_estreia) or not _data_valida(nova_data_saida):
        return None

    if not isinstance(nova_duracao, int) or isinstance(nova_duracao, bool) or nova_duracao <= 0:
        return None

    data_inicio = _parse_data(nova_data_estreia)
    data_fim = _parse_data(nova_data_saida)
    if data_inicio > data_fim:
        return None

    if any(
        outro.codigo != filme.codigo and outro.nome.lower() == novo_nome.lower()
        for outro in filmes
    ):
        return None

    filme.nome = novo_nome
    filme.data_estreia = data_inicio.strftime("%d-%m-%Y")
    filme.data_saida = data_fim.strftime("%d-%m-%Y")
    filme.duracao = nova_duracao
    if cartaz_url is not None:
        filme.cartaz_url = cartaz_url
    return filme


def remover_filme(codigo_filme):
    filme = pegar_filme(codigo_filme)
    if filme is None:
        return False

    sessoes[:] = [sessao for sessao in sessoes if sessao.filme.codigo != codigo_filme]
    filmes.remove(filme)
    return True


def atualizar_sala(numero, capacidade=None, tipo_sala_param=None):
    sala = pegar_sala(numero)
    if sala is None:
        return None

    nova_capacidade = sala.capacidade if capacidade is None else capacidade
    novo_tipo = sala.tipo if tipo_sala_param is None else tipo_sala_param

    if not isinstance(nova_capacidade, int) or isinstance(nova_capacidade, bool) or nova_capacidade <= 0:
        return None

    if not isinstance(novo_tipo, str) or novo_tipo not in ("2D", "3D"):
        return None

    sala.capacidade = nova_capacidade
    sala.tipo = novo_tipo
    return sala


def remover_sala(numero):
    sala = pegar_sala(numero)
    if sala is None:
        return False

    sessoes[:] = [sessao for sessao in sessoes if sessao.sala.numero != numero]
    salas.remove(sala)
    return True


def cadastrar_sessao(numero_sala, codigo_filme, data_sessao, hora_inicio):
    if not isinstance(numero_sala, int) or isinstance(numero_sala, bool):
        return None
    if not isinstance(codigo_filme, int) or isinstance(codigo_filme, bool):
        return None
    if not isinstance(hora_inicio, int) or isinstance(hora_inicio, bool):
        return None
    if not isinstance(data_sessao, str):
        return None

    data_sessao_padrao = _normalizar_data(data_sessao)
    if data_sessao_padrao is None:
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
            and _parse_data(sessao.data) == _parse_data(data_sessao_padrao)
            and sessao.hora_inicio == hora_inicio
        ):
            return None

    nova_sessao = Sessao(sala_encontrada, filme_encontrado, data_sessao_padrao, hora_inicio)
    nova_sessao.codigo = len(sessoes) + 1
    nova_sessao.assentos = {numero: 0 for numero in range(1, sala_encontrada.capacidade + 1)}
    sessoes.append(nova_sessao)
    return nova_sessao


def listar_filmes_por_data(data):
    data_padrao = _normalizar_data(data)
    if data_padrao is None:
        return "Data invalida."

    linhas = []
    for sessao in sorted(sessoes, key=lambda item: item.codigo):
        sessao_data = _normalizar_data(sessao.data)
        if sessao_data is None:
            continue
        if _parse_data(sessao_data) != _parse_data(data_padrao):
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


def atualizar_sessao(codigo_sessao, numero_sala=None, codigo_filme=None, data_sessao=None, hora_inicio=None):
    sessao = pegar_sessao(codigo_sessao)
    if sessao is None:
        return None

    nova_sala_numero = sessao.sala.numero if numero_sala is None else numero_sala
    novo_filme_codigo = sessao.filme.codigo if codigo_filme is None else codigo_filme
    nova_data = sessao.data if data_sessao is None else data_sessao
    nova_hora = sessao.hora_inicio if hora_inicio is None else hora_inicio

    if not isinstance(nova_sala_numero, int) or isinstance(nova_sala_numero, bool):
        return None
    if not isinstance(novo_filme_codigo, int) or isinstance(novo_filme_codigo, bool):
        return None
    if not isinstance(nova_hora, int) or isinstance(nova_hora, bool):
        return None
    if not isinstance(nova_data, str):
        return None

    nova_data_padrao = _normalizar_data(nova_data)
    if nova_data_padrao is None:
        return None
    if nova_hora < 0 or nova_hora > 23:
        return None

    sala_alvo = pegar_sala(nova_sala_numero)
    if sala_alvo is None:
        return None

    filme_alvo = pegar_filme(novo_filme_codigo)
    if filme_alvo is None:
        return None

    for outra in sessoes:
        if outra.codigo == codigo_sessao:
            continue
        if (
            outra.sala.numero == nova_sala_numero
            and _parse_data(outra.data) == _parse_data(nova_data_padrao)
            and outra.hora_inicio == nova_hora
        ):
            return None

    sessao.sala = sala_alvo
    sessao.filme = filme_alvo
    sessao.data = nova_data_padrao
    sessao.hora_inicio = nova_hora
    sessao.assentos = {numero: 0 for numero in range(1, sala_alvo.capacidade + 1)}
    return sessao


def remover_sessao(codigo_sessao):
    sessao = pegar_sessao(codigo_sessao)
    if sessao is None:
        return False

    sessoes.remove(sessao)
    return True


def removerIngressos(codigo_sessao, assentos):
    sessao = pegar_sessao(codigo_sessao)
    if sessao is None:
        return 0

    if not isinstance(assentos, list):
        return 0

    if not assentos:
        return 0

    if len(set(assentos)) != len(assentos):
        return 0

    for assento in assentos:
        if not isinstance(assento, int) or isinstance(assento, bool):
            return 0
        if assento <= 0 or assento > sessao.sala.capacidade:
            return 0
        if sessao.assentos.get(assento, 0) == 0:
            return 0

    for assento in assentos:
        sessao.assentos[assento] = 0

    return len(assentos)


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
