from fastapi import FastAPI
from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from controller import router
from database import init_db, load_state, save_state

app = FastAPI(
    title="Cinema API",
    version="1.0.0",
    description="API REST para cadastro de filmes, salas, sessões e compra de ingressos.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
app.include_router(router)
STATIC_DIR = Path(__file__).with_name("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup_event():
    init_db()
    load_state()


@app.get("/")
def read_root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/admin")
def read_admin():
    return FileResponse(STATIC_DIR / "admin.html")


@app.post("/persist")
def persist_state():
    save_state()
    return {"success": True, "message": "Estado salvo com sucesso."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
