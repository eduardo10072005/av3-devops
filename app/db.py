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
                CREATE TABLE IF NOT EXISTS itens (
                    id         SERIAL PRIMARY KEY,
                    titulo     TEXT NOT NULL,
                    descricao  TEXT NOT NULL DEFAULT '',
                    criado_em  TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                """
            )
    _schema_ready = True


def listar():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, titulo, descricao, criado_em FROM itens ORDER BY id DESC;")
            return cur.fetchall()


def buscar(item_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, titulo, descricao, criado_em FROM itens WHERE id = %s;",
                (item_id,),
            )
            return cur.fetchone()


def criar(titulo, descricao):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO itens (titulo, descricao) VALUES (%s, %s) RETURNING id;",
                (titulo, descricao),
            )
            return cur.fetchone()["id"]


def atualizar(item_id, titulo, descricao):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE itens SET titulo = %s, descricao = %s WHERE id = %s;",
                (titulo, descricao, item_id),
            )
            return cur.rowcount > 0


def excluir(item_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM itens WHERE id = %s;", (item_id,))
            return cur.rowcount > 0


def ping():
    """Usado pelo /healthz: levanta exceção se o banco não responde."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
