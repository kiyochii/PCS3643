"""Rotas REST de tipos ingresso."""

from fastapi import APIRouter, Response

from repositories import tipos_ingresso
from schemas import CodigoIngresso, TipoIngressoCadastro, TipoIngressoDados

router = APIRouter()


@router.get("/tipos-ingresso", tags=["Tipos de ingresso"])
def listar_tipos_ingresso():
    return tipos_ingresso.listar_tipos_ingresso()


@router.post("/tipos-ingresso", status_code=201, tags=["Tipos de ingresso"])
def cadastrar_tipo_ingresso(dados: TipoIngressoCadastro, response: Response):
    ingresso = tipos_ingresso.cadastrar_tipo_ingresso(**dados.model_dump())
    response.headers["Location"] = f"/tipos-ingresso/{ingresso.codigo}"
    return ingresso


@router.put("/tipos-ingresso/{codigo}", tags=["Tipos de ingresso"])
def editar_tipo_ingresso(codigo: CodigoIngresso, dados: TipoIngressoDados):
    """Edita um tipo existente. Para cadastrar primeiro, use POST /tipos-ingresso."""
    return tipos_ingresso.editar_tipo_ingresso(codigo, **dados.model_dump())


@router.delete("/tipos-ingresso/{codigo}", status_code=204, tags=["Tipos de ingresso"])
def remover_tipo_ingresso(codigo: CodigoIngresso):
    tipos_ingresso.remover_tipo_ingresso(codigo)
    return Response(status_code=204)
