
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
    if (filme != None):
        return filme
    return None
#metodos
