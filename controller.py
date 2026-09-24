from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Response, UploadFile
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field, HttpUrl

import cinema
from cinema import (
    atualizar_filme as atualizar_filme_fn,
    atualizar_sala as atualizar_sala_fn,
    atualizar_sessao as atualizar_sessao_fn,
    atualizar_valor_ingresso as atualizar_valor_ingresso_fn,
    comprarIngressos,
    cadastrar_filme as cadastrar_filme_fn,
    cadastrar_sala as cadastrar_sala_fn,
    cadastrar_sessao as cadastrar_sessao_fn,
    cadastrar_valor_ingresso as cadastrar_valor_ingresso_fn,
    listar_filmes_por_data as listar_filmes_por_data_fn,
    remover_filme as remover_filme_fn,
    remover_sala as remover_sala_fn,
    remover_sessao as remover_sessao_fn,
    remover_valor_ingresso as remover_valor_ingresso_fn,
    removerIngressos,
)
from database import load_cartaz, save_cartaz, save_state

router = APIRouter(prefix="/cinema", tags=["cinema"])
MAX_CARTAZ_BYTES = 5 * 1024 * 1024
MAX_CARTAZ_PIXELS = 25_000_000
CARTAZ_TYPES = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
CartazLocal = Annotated[str, Field(pattern=r"^/cinema/cartazes/[0-9a-f]{32}$")]


class ValorIngressoInput(BaseModel):
    tipo_sala: str
    valor_ingresso: int


class SalaInput(BaseModel):
    numero: int
    capacidade: int
    tipo_sala: str


class FilmeInput(BaseModel):
    codigo: int | None = None
    nome: str
    data_estreia: str
    data_saida: str
    duracao: int
    cartaz_url: HttpUrl | CartazLocal | None = None


class SessaoInput(BaseModel):
    codigo: int | None = None
    numero_sala: int
    codigo_filme: int
    data_sessao: str
    hora_inicio: int


class CompraIngressosInput(BaseModel):
    assentos: list[int]
    tipos_ingresso: list[int]


class RemoverIngressosInput(BaseModel):
    assentos: list[int]


def _persist_and_return(data: dict):
    save_state()
    return {"success": True, **data}


def _serializar_filme(filme):
    return {
        "codigo": filme.codigo,
        "nome": filme.nome,
        "data_estreia": filme.data_estreia,
        "data_saida": filme.data_saida,
        "duracao": filme.duracao,
        "cartaz_url": filme.cartaz_url,
    }


def _serializar_sala(sala):
    return {
        "numero": sala.numero,
        "capacidade": sala.capacidade,
        "tipo": sala.tipo,
    }


def _serializar_sessao(sessao):
    return {
        "codigo": sessao.codigo,
        "sala": _serializar_sala(sessao.sala),
        "filme": _serializar_filme(sessao.filme),
        "data": sessao.data,
        "hora_inicio": sessao.hora_inicio,
        "assentos": sessao.assentos,
    }


@router.post("/valor-ingresso")
def cadastrar_valor_ingresso_endpoint(payload: ValorIngressoInput):
    ok = cadastrar_valor_ingresso_fn(payload.tipo_sala, payload.valor_ingresso)
    if not ok:
        raise HTTPException(status_code=400, detail="Tipo de sala ou valor inválido.")

    return _persist_and_return({
        "tipo_sala": payload.tipo_sala,
        "valor_ingresso": payload.valor_ingresso,
    })


@router.put("/valor-ingresso/update/{tipo_sala_nome}")
def atualizar_valor_ingresso_endpoint(tipo_sala_nome: str, payload: ValorIngressoInput):
    ok = atualizar_valor_ingresso_fn(tipo_sala_nome, payload.valor_ingresso)
    if not ok:
        raise HTTPException(status_code=400, detail="Valor de ingresso inválido.")

    return _persist_and_return({
        "tipo_sala": tipo_sala_nome,
        "valor_ingresso": payload.valor_ingresso,
    })


@router.delete("/valor-ingresso/{tipo_sala_nome}")
def remover_valor_ingresso_endpoint(tipo_sala_nome: str):
    ok = remover_valor_ingresso_fn(tipo_sala_nome)
    if not ok:
        raise HTTPException(status_code=404, detail="Tipo de sala não encontrado.")

    return _persist_and_return({"tipo_sala": tipo_sala_nome})


@router.post("/salas")
def cadastrar_sala_endpoint(payload: SalaInput):
    sala = cadastrar_sala_fn(payload.numero, payload.capacidade, payload.tipo_sala)
    if sala is None:
        raise HTTPException(status_code=400, detail="Sala inválida.")

    return _persist_and_return({"sala": _serializar_sala(sala)})


@router.put("/salas/update/{numero_sala}")
def atualizar_sala_endpoint(numero_sala: int, payload: SalaInput):
    sala = atualizar_sala_fn(numero_sala, payload.capacidade, payload.tipo_sala)
    if sala is None:
        raise HTTPException(status_code=400, detail="Sala inválida para atualização.")

    return _persist_and_return({"sala": _serializar_sala(sala)})


@router.delete("/salas/{numero_sala}")
def remover_sala_endpoint(numero_sala: int):
    ok = remover_sala_fn(numero_sala)
    if not ok:
        raise HTTPException(status_code=404, detail="Sala não encontrada.")

    return _persist_and_return({"numero_sala": numero_sala})


@router.post("/filmes")
def cadastrar_filme_endpoint(payload: FilmeInput):
    filme = cadastrar_filme_fn(
        payload.nome,
        payload.data_estreia,
        payload.data_saida,
        payload.duracao,
        str(payload.cartaz_url) if payload.cartaz_url else None,
    )
    if filme is None:
        raise HTTPException(status_code=400, detail="Filme inválido.")

    return _persist_and_return({"filme": _serializar_filme(filme)})


@router.put("/filmes/update/{codigo_filme}")
def atualizar_filme_endpoint(codigo_filme: int, payload: FilmeInput):
    filme = atualizar_filme_fn(
        codigo_filme,
        payload.nome,
        payload.data_estreia,
        payload.data_saida,
        payload.duracao,
        str(payload.cartaz_url) if payload.cartaz_url else None,
    )
    if filme is None:
        raise HTTPException(status_code=400, detail="Filme inválido para atualização.")

    return _persist_and_return({"filme": _serializar_filme(filme)})


@router.delete("/filmes/{codigo_filme}")
def remover_filme_endpoint(codigo_filme: int):
    ok = remover_filme_fn(codigo_filme)
    if not ok:
        raise HTTPException(status_code=404, detail="Filme não encontrado.")

    return _persist_and_return({"codigo_filme": codigo_filme})


@router.post("/filmes/{codigo_filme}/cartaz")
def enviar_cartaz(codigo_filme: int, arquivo: UploadFile = File(...)):
    filme = cinema.pegar_filme(codigo_filme)
    if filme is None:
        raise HTTPException(status_code=404, detail="Filme não encontrado.")

    conteudo = arquivo.file.read(MAX_CARTAZ_BYTES + 1)
    if len(conteudo) > MAX_CARTAZ_BYTES:
        raise HTTPException(status_code=413, detail="O cartaz deve ter no máximo 5 MB.")
    if not conteudo:
        raise HTTPException(status_code=400, detail="O arquivo do cartaz está vazio.")

    try:
        with Image.open(BytesIO(conteudo)) as imagem:
            tipo = CARTAZ_TYPES.get(imagem.format)
            if tipo is None:
                raise HTTPException(status_code=415, detail="Envie um cartaz JPEG, PNG ou WebP.")
            if imagem.width * imagem.height > MAX_CARTAZ_PIXELS:
                raise HTTPException(status_code=413, detail="O cartaz deve ter no máximo 25 megapixels.")
            imagem.verify()
        # A decodificação também detecta imagens truncadas que têm um cabeçalho válido.
        with Image.open(BytesIO(conteudo)) as imagem:
            imagem.load()
    except Image.DecompressionBombError:
        raise HTTPException(status_code=413, detail="As dimensões do cartaz são muito grandes.")
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
        raise HTTPException(status_code=415, detail="O arquivo enviado não é uma imagem válida.")

    save_cartaz(filme, conteudo, tipo)
    return {"success": True, "filme": _serializar_filme(filme)}


@router.get("/cartazes/{cartaz_id}")
def obter_cartaz(cartaz_id: str):
    cartaz = load_cartaz(cartaz_id)
    if cartaz is None:
        raise HTTPException(status_code=404, detail="Cartaz não encontrado.")
    conteudo, tipo = cartaz
    return Response(content=conteudo, media_type=tipo,
                    headers={"X-Content-Type-Options": "nosniff"})


@router.post("/sessoes")
def cadastrar_sessao_endpoint(payload: SessaoInput):
    sessao = cadastrar_sessao_fn(
        payload.numero_sala,
        payload.codigo_filme,
        payload.data_sessao,
        payload.hora_inicio,
    )
    if sessao is None:
        raise HTTPException(status_code=400, detail="Sessão inválida.")

    return _persist_and_return({"sessao": _serializar_sessao(sessao)})


@router.put("/sessoes/update/{codigo_sessao}")
def atualizar_sessao_endpoint(codigo_sessao: int, payload: SessaoInput):
    sessao = atualizar_sessao_fn(
        codigo_sessao,
        payload.numero_sala,
        payload.codigo_filme,
        payload.data_sessao,
        payload.hora_inicio,
    )
    if sessao is None:
        raise HTTPException(status_code=400, detail="Sessão inválida para atualização.")

    return _persist_and_return({"sessao": _serializar_sessao(sessao)})


@router.delete("/sessoes/{codigo_sessao}")
def remover_sessao_endpoint(codigo_sessao: int):
    ok = remover_sessao_fn(codigo_sessao)
    if not ok:
        raise HTTPException(status_code=404, detail="Sessão não encontrada.")

    return _persist_and_return({"codigo_sessao": codigo_sessao})


@router.get("/filmes/data/{data}")
def listar_filmes_por_data(data: str):
    resultado = listar_filmes_por_data_fn(data)
    return {"data": data, "resultado": resultado}


@router.get("/sessoes")
def listar_sessoes():
    return {"sessoes": [_serializar_sessao(sessao) for sessao in cinema.sessoes]}


@router.get("/filmes")
def listar_filmes():
    return {"filmes": [_serializar_filme(filme) for filme in cinema.filmes]}


@router.get("/salas")
def listar_salas():
    return {"salas": [_serializar_sala(sala) for sala in cinema.salas]}


@router.get("/valor-ingresso")
def listar_valores():
    return {"tipo_sala": cinema.tipo_sala}


@router.get("/tipos-ingresso")
def listar_tipos_ingresso():
    return {"tipos_ingresso": [
        {"codigo": 0, "nome": "Inteira", "fator": 1},
        {"codigo": 1, "nome": "Meia-entrada", "fator": 0.5},
    ]}


@router.post("/sessoes/{codigo_sessao}/ingressos")
def comprar_ingressos(codigo_sessao: int, payload: CompraIngressosInput):
    total = comprarIngressos(codigo_sessao, payload.assentos, payload.tipos_ingresso)
    if total == 0:
        raise HTTPException(status_code=400, detail="Compra inválida.")

    return _persist_and_return({
        "codigo_sessao": codigo_sessao,
        "total": total,
        "assentos": payload.assentos,
        "tipos_ingresso": payload.tipos_ingresso,
    })


@router.delete("/sessoes/{codigo_sessao}/ingressos")
def remover_ingressos(codigo_sessao: int, payload: RemoverIngressosInput):
    removidos = removerIngressos(codigo_sessao, payload.assentos)
    if removidos == 0:
        raise HTTPException(status_code=400, detail="Nenhum ingresso removido. Verifique os assentos.")

    return _persist_and_return({
        "codigo_sessao": codigo_sessao,
        "assentos_removidos": removidos,
        "assentos": payload.assentos,
    })
