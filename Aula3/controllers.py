"""Controladores REST: validam a entrada e chamam o modelo do cinema."""

from datetime import datetime
import re
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Path, Response
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator

import cinema


def validar_data(valor: str) -> str:
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", valor):
        raise ValueError("Use uma data no formato dd/mm/aaaa.")
    try:
        datetime.strptime(valor, "%d/%m/%Y")
    except ValueError as erro:
        raise ValueError("Informe uma data válida.") from erro
    return valor


Data = Annotated[str, AfterValidator(validar_data)]
Positivo = Annotated[int, Field(strict=True, gt=0, le=2147483647)]
NaoNegativo = Annotated[int, Field(strict=True, ge=0, le=2147483647)]
TipoSala = Literal["2D", "3D"]
Identificador = Annotated[int, Path(gt=0, le=2147483647)]
CodigoIngresso = Annotated[int, Path(ge=0, le=2147483647)]


class Entrada(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class FilmeDados(Entrada):
    nome: str = Field(min_length=1, examples=["Central do Brasil"])
    data_estreia: Data = Field(examples=["01/09/2026"])
    data_saida: Data = Field(examples=["30/09/2026"])
    duracao: Positivo = Field(examples=[110])

    @model_validator(mode="after")
    def validar_periodo(self):
        inicio = datetime.strptime(self.data_estreia, "%d/%m/%Y")
        fim = datetime.strptime(self.data_saida, "%d/%m/%Y")
        if fim < inicio:
            raise ValueError("A data de saída não pode ser anterior à estreia.")
        return self


class SalaDados(Entrada):
    capacidade: Positivo = Field(examples=[100])
    tipo_sala: TipoSala


class SalaCadastro(SalaDados):
    numero: Positivo = Field(examples=[1])


class SessaoDados(Entrada):
    numero_sala: Positivo = Field(examples=[1])
    codigo_filme: Positivo = Field(examples=[1])
    data_sessao: Data = Field(examples=["17/09/2026"])
    hora_inicio: int = Field(strict=True, ge=0, le=23, examples=[15])


class TipoIngressoDados(Entrada):
    nome: str = Field(min_length=1, examples=["Inteira"])
    percentual: int = Field(strict=True, ge=1, le=100, examples=[100])


class TipoIngressoCadastro(TipoIngressoDados):
    codigo: NaoNegativo = Field(examples=[0])


class PrecoDados(Entrada):
    valor_ingresso: Positivo = Field(examples=[30])


class PrecoCadastro(PrecoDados):
    tipo_sala: TipoSala


router = APIRouter()


@router.get("/filmes", tags=["Filmes"])
def listar_filmes():
    return cinema.listar_filmes()


@router.post("/filmes", status_code=201, tags=["Filmes"])
def cadastrar_filme(dados: FilmeDados, response: Response):
    filme = cinema.cadastrar_filme(**dados.model_dump())
    response.headers["Location"] = f"/filmes/{filme.codigo}"
    return filme


@router.put("/filmes/{codigo}", tags=["Filmes"])
def editar_filme(codigo: Identificador, dados: FilmeDados):
    """Edita um filme existente. Para cadastrar primeiro, use POST /filmes."""
    return cinema.editar_filme(codigo, **dados.model_dump())


@router.delete("/filmes/{codigo}", status_code=204, tags=["Filmes"])
def remover_filme(codigo: Identificador):
    cinema.remover_filme(codigo)
    return Response(status_code=204)


@router.get("/salas", tags=["Salas"])
def listar_salas():
    return cinema.listar_salas()


@router.post("/salas", status_code=201, tags=["Salas"])
def cadastrar_sala(dados: SalaCadastro, response: Response):
    sala = cinema.cadastrar_sala(**dados.model_dump())
    if sala is None:
        raise HTTPException(status_code=400, detail="Sala inválida ou número já cadastrado.")
    response.headers["Location"] = f"/salas/{sala.numero}"
    return sala


@router.put("/salas/{numero}", tags=["Salas"])
def editar_sala(numero: Identificador, dados: SalaDados):
    """Edita uma sala existente. Para cadastrar primeiro, use POST /salas."""
    return cinema.editar_sala(numero, **dados.model_dump())


@router.delete("/salas/{numero}", status_code=204, tags=["Salas"])
def remover_sala(numero: Identificador):
    cinema.remover_sala(numero)
    return Response(status_code=204)


@router.get("/sessoes", tags=["Sessões"])
def listar_sessoes():
    return cinema.listar_sessoes()


@router.post("/sessoes", status_code=201, tags=["Sessões"])
def cadastrar_sessao(dados: SessaoDados, response: Response):
    sessao = cinema.cadastrar_sessao(**dados.model_dump())
    if sessao is None:
        raise HTTPException(status_code=400, detail="Sessão inválida: confira a sala, o filme e se o horário já está ocupado.")
    response.headers["Location"] = f"/sessoes/{sessao.codigo}"
    return sessao


@router.put("/sessoes/{codigo}", tags=["Sessões"])
def editar_sessao(codigo: Identificador, dados: SessaoDados):
    """Edita uma sessão existente. Para cadastrar primeiro, use POST /sessoes."""
    return cinema.editar_sessao(codigo, **dados.model_dump())


@router.delete("/sessoes/{codigo}", status_code=204, tags=["Sessões"])
def remover_sessao(codigo: Identificador):
    cinema.remover_sessao(codigo)
    return Response(status_code=204)


@router.get("/tipos-ingresso", tags=["Tipos de ingresso"])
def listar_tipos_ingresso():
    return cinema.listar_tipos_ingresso()


@router.post("/tipos-ingresso", status_code=201, tags=["Tipos de ingresso"])
def cadastrar_tipo_ingresso(dados: TipoIngressoCadastro, response: Response):
    ingresso = cinema.cadastrar_tipo_ingresso(**dados.model_dump())
    response.headers["Location"] = f"/tipos-ingresso/{ingresso.codigo}"
    return ingresso


@router.put("/tipos-ingresso/{codigo}", tags=["Tipos de ingresso"])
def editar_tipo_ingresso(codigo: CodigoIngresso, dados: TipoIngressoDados):
    """Edita um tipo existente. Para cadastrar primeiro, use POST /tipos-ingresso."""
    return cinema.editar_tipo_ingresso(codigo, **dados.model_dump())


@router.delete("/tipos-ingresso/{codigo}", status_code=204, tags=["Tipos de ingresso"])
def remover_tipo_ingresso(codigo: CodigoIngresso):
    cinema.remover_tipo_ingresso(codigo)
    return Response(status_code=204)


@router.get("/precos", response_model=list[PrecoCadastro], tags=["Preços"])
def listar_precos():
    return cinema.listar_precos()


@router.post("/precos", response_model=PrecoCadastro, status_code=201, tags=["Preços"])
def cadastrar_preco(dados: PrecoCadastro, response: Response):
    sucesso = cinema.cadastrar_valor_ingresso({"tipo": dados.tipo_sala}, dados.valor_ingresso)
    if not sucesso:
        raise HTTPException(status_code=400, detail="Tipo de sala ou valor de ingresso inválido.")
    response.headers["Location"] = f"/precos/{dados.tipo_sala}"
    return dados.model_dump()


@router.put("/precos/{tipo_sala}", response_model=PrecoCadastro, tags=["Preços"])
def editar_preco(tipo_sala: TipoSala, dados: PrecoDados):
    """Edita um preço existente. Para cadastrar primeiro, use POST /precos."""
    return cinema.editar_valor_ingresso(tipo_sala, **dados.model_dump())


@router.delete("/precos/{tipo_sala}", status_code=204, tags=["Preços"])
def remover_preco(tipo_sala: TipoSala):
    cinema.remover_valor_ingresso(tipo_sala)
    return Response(status_code=204)
