###listas
#filmes
#salas
#sessoes

###dictionary
#tipo_sala

class Filme:

    def __init__(self, nome=None, data_estreia=None, data_saida=None, duracao=None):
#        self.codigo
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

#metodos
