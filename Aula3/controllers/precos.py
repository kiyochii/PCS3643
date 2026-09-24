"""Rotas REST de precos."""

from fastapi import APIRouter, HTTPException, Response

from repositories import precos
from schemas import PrecoCadastro, PrecoDados, TipoSala

router = APIRouter()


@router.get("/precos", response_model=list[PrecoCadastro], tags=["Preços"])
def listar_precos():
    return precos.listar_precos()


@router.post("/precos", response_model=PrecoCadastro, status_code=201, tags=["Preços"])
def cadastrar_preco(dados: PrecoCadastro, response: Response):
    sucesso = precos.cadastrar_valor_ingresso({"tipo": dados.tipo_sala}, dados.valor_ingresso)
    if not sucesso:
        raise HTTPException(status_code=400, detail="Tipo de sala ou valor de ingresso inválido.")
    response.headers["Location"] = f"/precos/{dados.tipo_sala}"
    return dados.model_dump()


@router.put("/precos/{tipo_sala}", response_model=PrecoCadastro, tags=["Preços"])
def editar_preco(tipo_sala: TipoSala, dados: PrecoDados):
    """Edita um preço existente. Para cadastrar primeiro, use POST /precos."""
    return precos.editar_valor_ingresso(tipo_sala, **dados.model_dump())


@router.delete("/precos/{tipo_sala}", status_code=204, tags=["Preços"])
def remover_preco(tipo_sala: TipoSala):
    precos.remover_valor_ingresso(tipo_sala)
    return Response(status_code=204)
