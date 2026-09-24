"""Entidade Sessao do cinema."""


class Sessao:
    def __init__(self, sala=None, filme=None, data=None, hora_inicio=None):
#        self.codigo
        self.sala = sala
        self.filme = filme
        self.data = data
        self.hora_inicio = hora_inicio
