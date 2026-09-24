"""Entidades e erros do domínio do cinema."""

from .errors import Conflito, NaoEncontrado
from .filme import Filme
from .sala import Sala
from .sessao import Sessao
from .tipo_ingresso import TipoIngresso

__all__ = ["Filme", "Sala", "Sessao", "TipoIngresso", "NaoEncontrado", "Conflito"]
