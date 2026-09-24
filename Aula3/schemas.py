"""Esquemas de entrada e validação dos dados da API."""

from datetime import datetime
import re
from typing import Annotated, Literal

from fastapi import Path
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator


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
