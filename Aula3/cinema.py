"""Compatibilidade com os imports originais; implementação separada por responsabilidade."""

from models import Conflito, Filme, NaoEncontrado, Sala, Sessao, TipoIngresso
from repositories.filmes import (
    cadastrar_filme,
    listar_filmes,
    editar_filme,
    remover_filme,
)
from repositories.salas import (
    cadastrar_sala,
    listar_salas,
    editar_sala,
    remover_sala,
)
from repositories.sessoes import (
    cadastrar_sessao,
    listar_sessoes,
    editar_sessao,
    remover_sessao,
)
from repositories.tipos_ingresso import (
    listar_tipos_ingresso,
    cadastrar_tipo_ingresso,
    editar_tipo_ingresso,
    remover_tipo_ingresso,
)
from repositories.precos import (
    cadastrar_valor_ingresso,
    listar_precos,
    editar_valor_ingresso,
    remover_valor_ingresso,
)

__all__ = [
    "Filme",
    "Sala",
    "Sessao",
    "TipoIngresso",
    "NaoEncontrado",
    "Conflito",
    "cadastrar_filme",
    "listar_filmes",
    "editar_filme",
    "remover_filme",
    "cadastrar_sala",
    "listar_salas",
    "editar_sala",
    "remover_sala",
    "cadastrar_sessao",
    "listar_sessoes",
    "editar_sessao",
    "remover_sessao",
    "listar_tipos_ingresso",
    "cadastrar_tipo_ingresso",
    "editar_tipo_ingresso",
    "remover_tipo_ingresso",
    "cadastrar_valor_ingresso",
    "listar_precos",
    "editar_valor_ingresso",
    "remover_valor_ingresso",
]
