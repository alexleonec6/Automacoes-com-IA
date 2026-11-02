import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "automacoes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            origem TEXT NOT NULL,
            categoria TEXT NOT NULL,
            urgencia TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            resposta_ia TEXT,
            notificado_telegram INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def salvar_evento(origem: str, categoria: str, urgencia: str, conteudo: str, resposta_ia: Optional[str] = None, notificado: bool = False) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO eventos (timestamp, origem, categoria, urgencia, conteudo, resposta_ia, notificado_telegram)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        origem,
        categoria,
        urgencia,
        conteudo,
        resposta_ia,
        1 if notificado else 0
    ))
    evento_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return evento_id

def listar_eventos(limite: int = 10) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eventos ORDER BY id DESC LIMIT ?", (limite,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
