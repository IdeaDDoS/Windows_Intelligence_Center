"""Camada de acesso ao SQLite local: conexão e inicialização do schema.

Mantém o produto local-first — o banco é um único arquivo na máquina. O DDL vive
versionado em ``database/schema.sql`` (fonte canônica do schema); este módulo só
abre conexões e aplica o schema na subida.
"""

from __future__ import annotations

import sqlite3

from config import settings

# Versão atual do schema (incrementa a cada mudança de DDL).
SCHEMA_VERSION = 1
# DDL versionado, ao lado do arquivo .db.
_SCHEMA_FILE = settings.db_path.parent / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão SQLite com acesso por nome de coluna e PRAGMAs locais."""
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db() -> None:
    """Cria o arquivo .db (se preciso) e aplica o schema versionado na subida."""
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    ddl = _SCHEMA_FILE.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(ddl)
        # Registra a versão atual apenas na primeira aplicação.
        row = conn.execute("SELECT MAX(version) AS v FROM schema_meta").fetchone()
        if row["v"] is None:
            conn.execute(
                "INSERT INTO schema_meta (version) VALUES (?)", (SCHEMA_VERSION,)
            )
        conn.commit()
