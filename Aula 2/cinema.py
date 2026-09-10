
###listas
filmes = []
salas = []
sessoes = []

###dictionary
tipo_sala = {}

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
#        self.assentos


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

    tipo_sala[tipo] = valor_ingresso
    return True


def cadastrar_sala(numero, capacidade, tipo_sala):
    if not isinstance(numero, int) or isinstance(numero, bool) or numero <= 0:
        return None

    if not isinstance(capacidade, int) or isinstance(capacidade, bool) or capacidade <= 0:
        return None

    if tipo_sala not in ("2D", "3D"):
        return None

    if any(sala.numero == numero for sala in salas):
        return None

    sala = Sala(numero, capacidade, tipo_sala)
    salas.append(sala)
    return sala

            
def cadastrar_filme(nome, data_estreia, data_saida, duracao):
    num = len(filmes)
    filme = Filme(num+1, nome, data_estreia, data_saida, duracao)
    if filme is not None:
        filmes.append(filme)
        return filme
    return None

#metodos
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

    # 3. Buscar a sala pelo número
    sala_encontrada = None
    for sala in salas:
        if sala.numero == numero_sala:
            sala_encontrada = sala
            break

    if sala_encontrada is None:
        return None

    # 4. Buscar o filme pelo código
    filme_encontrado = None
    for filme in filmes:
        if filme.codigo == codigo_filme:
            filme_encontrado = filme
            break

    if filme_encontrado is None:
        return None

    # 5. Verificar se já existe uma sessão na mesma sala, data e hora de início
    for sessao in sessoes:
        if (
            sessao.sala.numero == numero_sala
            and sessao.data == data_sessao
            and sessao.hora_inicio == hora_inicio
        ):
            return None

    # 6. Criar o objeto da sessão
    nova_sessao = Sessao(
        sala_encontrada,
        filme_encontrado,
        data_sessao,
        hora_inicio
    )

    # 7. Gerar um código sequencial para a sessão, começando em 1
    nova_sessao.codigo = max(
        (sessao.codigo for sessao in sessoes),
        default=0
    ) + 1

    # 8. Numerar os assentos de 1 até a capacidade da sala e inicializá-los com 0
    nova_sessao.assentos = {}
    for numero in range(1, sala_encontrada.capacidade + 1):
        nova_sessao.assentos[numero] = 0

    # 9. Adicionar a sessão à lista e retornar o objeto criado
    sessoes.append(nova_sessao)
    return nova_sessao