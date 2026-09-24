"""Rotas REST de sessoes."""

from fastapi import APIRouter, HTTPException, Response

from repositories import sessoes
from schemas import Identificador, SessaoDados

router = APIRouter()


@router.get("/sessoes", tags=["Sessões"])
def listar_sessoes():
    return sessoes.listar_sessoes()


@router.post("/sessoes", status_code=201, tags=["Sessões"])
def cadastrar_sessao(dados: SessaoDados, response: Response):
    sessao = sessoes.cadastrar_sessao(**dados.model_dump())
    if sessao is None:
        raise HTTPException(status_code=400, detail="Sessão inválida: confira a sala, o filme e se o horário já está ocupado.")
    response.headers["Location"] = f"/sessoes/{sessao.codigo}"
    return sessao


@router.put("/sessoes/{codigo}", tags=["Sessões"])
def editar_sessao(codigo: Identificador, dados: SessaoDados):
    """Edita uma sessão existente. Para cadastrar primeiro, use POST /sessoes."""
    return sessoes.editar_sessao(codigo, **dados.model_dump())


@router.delete("/sessoes/{codigo}", status_code=204, tags=["Sessões"])
def remover_sessao(codigo: Identificador):
    sessoes.remover_sessao(codigo)
    return Response(status_code=204)
