"""Entidade TipoIngresso do cinema."""


class TipoIngresso:
    def __init__(self, codigo, nome, percentual):
        self.codigo = codigo
        self.nome = nome
        self.percentual = percentual
