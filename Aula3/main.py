"""Inicialização da API e da documentação interativa do cinema."""

from contextlib import asynccontextmanager
import sqlite3

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from models import Conflito, NaoEncontrado
from controllers import router
from database import criar_tabelas


@asynccontextmanager
async def lifespan(app: FastAPI):
    criar_tabelas()
    yield


app = FastAPI(title="Cinema Aula3 MVC", lifespan=lifespan)
app.include_router(router)


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return RedirectResponse(url="/docs")


@app.exception_handler(NaoEncontrado)
async def nao_encontrado(request: Request, erro: NaoEncontrado):
    return JSONResponse(status_code=404, content={"detail": str(erro)})


@app.exception_handler(Conflito)
async def conflito(request: Request, erro: Conflito):
    return JSONResponse(status_code=409, content={"detail": str(erro)})


@app.exception_handler(sqlite3.IntegrityError)
async def integridade(request: Request, erro: sqlite3.IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Operação não permitida: dados duplicados ou vinculados a outro cadastro."},
    )
