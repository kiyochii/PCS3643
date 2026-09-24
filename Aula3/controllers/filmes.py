"""Rotas REST de filmes."""

from fastapi import APIRouter, Response

from repositories import filmes
from schemas import FilmeDados, Identificador

router = APIRouter()


@router.get("/filmes", tags=["Filmes"])
def listar_filmes():
    return filmes.listar_filmes()


@router.post("/filmes", status_code=201, tags=["Filmes"])
def cadastrar_filme(dados: FilmeDados, response: Response):
    filme = filmes.cadastrar_filme(**dados.model_dump())
    response.headers["Location"] = f"/filmes/{filme.codigo}"
    return filme


@router.put("/filmes/{codigo}", tags=["Filmes"])
def editar_filme(codigo: Identificador, dados: FilmeDados):
    """Edita um filme existente. Para cadastrar primeiro, use POST /filmes."""
    return filmes.editar_filme(codigo, **dados.model_dump())


@router.delete("/filmes/{codigo}", status_code=204, tags=["Filmes"])
def remover_filme(codigo: Identificador):
    filmes.remover_filme(codigo)
    return Response(status_code=204)
