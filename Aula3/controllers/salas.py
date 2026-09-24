"""Rotas REST de salas."""

from fastapi import APIRouter, HTTPException, Response

from repositories import salas
from schemas import Identificador, SalaCadastro, SalaDados

router = APIRouter()


@router.get("/salas", tags=["Salas"])
def listar_salas():
    return salas.listar_salas()


@router.post("/salas", status_code=201, tags=["Salas"])
def cadastrar_sala(dados: SalaCadastro, response: Response):
    sala = salas.cadastrar_sala(**dados.model_dump())
    if sala is None:
        raise HTTPException(status_code=400, detail="Sala inválida ou número já cadastrado.")
    response.headers["Location"] = f"/salas/{sala.numero}"
    return sala


@router.put("/salas/{numero}", tags=["Salas"])
def editar_sala(numero: Identificador, dados: SalaDados):
    """Edita uma sala existente. Para cadastrar primeiro, use POST /salas."""
    return salas.editar_sala(numero, **dados.model_dump())


@router.delete("/salas/{numero}", status_code=204, tags=["Salas"])
def remover_sala(numero: Identificador):
    salas.remover_sala(numero)
    return Response(status_code=204)
