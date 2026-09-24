import json
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4

import cinema

DB_PATH = Path(__file__).with_name("cinema.db")


def _to_plain(obj):
    if isinstance(obj, dict):
        return {key: _to_plain(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [_to_plain(item) for item in obj]
    if hasattr(obj, "__dict__"):
        return {key: _to_plain(value) for key, value in obj.__dict__.items()}
    return obj


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        _init_cartazes(conn)
    return DB_PATH


def _init_cartazes(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS cartazes (
            id TEXT PRIMARY KEY,
            conteudo BLOB NOT NULL,
            tipo TEXT NOT NULL
        )
        """
    )


def _save_state(conn):
    payload = {
        "filmes": _to_plain(cinema.filmes),
        "salas": _to_plain(cinema.salas),
        "sessoes": _to_plain(cinema.sessoes),
        "tipo_sala": cinema.tipo_sala,
    }

    conn.execute(
        "INSERT INTO app_state(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        ("cinema_state", json.dumps(payload, ensure_ascii=False)),
    )
    urls = {filme.cartaz_url for filme in cinema.filmes}
    unused = [(row[0],) for row in conn.execute("SELECT id FROM cartazes")
              if f"/cinema/cartazes/{row[0]}" not in urls]
    conn.executemany("DELETE FROM cartazes WHERE id = ?", unused)


def save_state():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        _save_state(conn)


def save_cartaz(filme, conteudo, tipo):
    """Grava a imagem e sua associação ao filme na mesma transação."""
    cartaz_id = uuid4().hex
    previous_url = filme.cartaz_url
    try:
        with closing(sqlite3.connect(DB_PATH)) as conn, conn:
            conn.execute(
                "INSERT INTO cartazes(id, conteudo, tipo) VALUES (?, ?, ?)",
                (cartaz_id, conteudo, tipo),
            )
            filme.cartaz_url = f"/cinema/cartazes/{cartaz_id}"
            _save_state(conn)
    except Exception:
        filme.cartaz_url = previous_url
        raise


def load_cartaz(cartaz_id):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        return conn.execute(
            "SELECT conteudo, tipo FROM cartazes WHERE id = ?", (cartaz_id,)
        ).fetchone()


def load_state():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        row = conn.execute(
            "SELECT value FROM app_state WHERE key = ?",
            ("cinema_state",),
        ).fetchone()

    if row is None:
        return False

    try:
        payload = json.loads(row[0])
    except (TypeError, ValueError):
        return False

    cinema.filmes.clear()
    cinema.salas.clear()
    cinema.sessoes.clear()
    cinema.tipo_sala.clear()

    for item in payload.get("filmes", []):
        filme = cinema.Filme(
            item.get("codigo"),
            item.get("nome"),
            item.get("data_estreia"),
            item.get("data_saida"),
            item.get("duracao"),
            item.get("cartaz_url"),
        )
        filme.codigo = item.get("codigo")
        cinema.filmes.append(filme)

    for item in payload.get("salas", []):
        sala = cinema.Sala(item.get("numero"), item.get("capacidade"), item.get("tipo"))
        cinema.salas.append(sala)

    for item in payload.get("sessoes", []):
        sala = next((s for s in cinema.salas if s.numero == item["sala"]["numero"]), None)
        filme = next((f for f in cinema.filmes if f.codigo == item["filme"]["codigo"]), None)
        sessao = cinema.Sessao(sala, filme, item.get("data"), item.get("hora_inicio"))
        sessao.codigo = item.get("codigo")
        sessao.assentos = item.get("assentos", {})
        cinema.sessoes.append(sessao)

    cinema.tipo_sala.update(payload.get("tipo_sala", {}))
    return True
