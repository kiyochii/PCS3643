import json
from pathlib import Path

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
    import sqlite3

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()
        return DB_PATH
    except sqlite3.DatabaseError:
        if DB_PATH.exists():
            DB_PATH.unlink()
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()
        return DB_PATH


def save_state():
    import sqlite3

    payload = {
        "filmes": _to_plain(cinema.filmes),
        "salas": _to_plain(cinema.salas),
        "sessoes": _to_plain(cinema.sessoes),
        "tipo_sala": cinema.tipo_sala,
    }

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO app_state(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        ("cinema_state", json.dumps(payload, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()


def load_state():
    import sqlite3

    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT value FROM app_state WHERE key = ?",
            ("cinema_state",),
        ).fetchone()
        conn.close()
    except sqlite3.DatabaseError:
        if DB_PATH.exists():
            DB_PATH.unlink()
        init_db()
        return False

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
