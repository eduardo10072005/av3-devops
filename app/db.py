"""Acesso ao PostgreSQL da Aiven. Toda a lógica de SQL fica aqui."""

import os

import psycopg2
from psycopg2.extras import RealDictCursor

_schema_ready = False


def get_connection():
    """Abre uma conexão nova. A URI vem da variável de ambiente AIVEN_DB_URL."""
    url = os.environ.get("AIVEN_DB_URL")
    if not url:
        raise RuntimeError("AIVEN_DB_URL não configurada")
    return psycopg2.connect(url, cursor_factory=RealDictCursor, connect_timeout=10)


def ensure_schema():
    """Cria a tabela na primeira vez que o app é usado."""
    global _schema_ready
    if _schema_ready:
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS filmes (
                    id         SERIAL PRIMARY KEY,
                    titulo     TEXT NOT NULL,
                    ano        INTEGER NOT NULL,
                    genero     TEXT NOT NULL,
                    assistido  TEXT NOT NULL
                );
                """
            )
    _schema_ready = True


def listar():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, ano, genero, assistido FROM filmes ORDER BY id DESC;")
            return cur.fetchall()


def buscar(item_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, titulo, ano, genero, assistido FROM filmes WHERE id = %s;",
                (item_id,),
            )
            return cur.fetchone()


def criar(titulo, ano, genero, assistido):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO filmes (titulo, ano, genero, assistido) VALUES (%s, %s, %s, %s) RETURNING id;",
                (titulo, ano, genero, assistido),
            )
            return cur.fetchone()["id"]


def atualizar(item_id, titulo, ano, genero, assistido):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE filmes SET titulo = %s, ano = %s, genero = %s, assistido = %s WHERE id = %s;",
                (titulo, ano, genero, assistido, item_id),
            )
            return cur.rowcount > 0


def excluir(item_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM filmes WHERE id = %s;", (item_id,))
            return cur.rowcount > 0


def ping():
    """Usado pelo /healthz: levanta exceção se o banco não responde."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
