"""Agrega os controladores REST de cada recurso."""

from fastapi import APIRouter

from . import filmes, precos, salas, sessoes, tipos_ingresso

router = APIRouter()
router.include_router(filmes.router)
router.include_router(salas.router)
router.include_router(sessoes.router)
router.include_router(tipos_ingresso.router)
router.include_router(precos.router)
