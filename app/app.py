"""
Aplicação CRUD — modelo do Projeto 0.

Tema padrão: lista de itens (título + descrição). A equipe adapta o tema
(equipamentos, estoque, reservas...) trocando os nomes de campos em db.py e
nos templates, mantendo as quatro operações de CRUD e o /healthz.
"""

import logging

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

import db

app = Flask(__name__)
app.logger.setLevel(logging.INFO)


@app.before_request
def preparar_banco():
    # O health check testa o banco por conta própria e não pode falhar aqui.
    if request.path != "/healthz":
        db.ensure_schema()


@app.route("/")
def index():
    return render_template("index.html", itens=db.listar())


@app.route("/itens", methods=["POST"])
def criar():
    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    if not titulo:
        abort(400, "O título é obrigatório.")
    db.criar(titulo, descricao)
    return redirect(url_for("index"))


@app.route("/itens/<int:item_id>/editar")
def editar(item_id):
    item = db.buscar(item_id)
    if item is None:
        abort(404)
    return render_template("editar.html", item=item)


@app.route("/itens/<int:item_id>", methods=["POST"])
def atualizar(item_id):
    titulo = request.form.get("titulo", "").strip()
    descricao = request.form.get("descricao", "").strip()
    if not titulo:
        abort(400, "O título é obrigatório.")
    if not db.atualizar(item_id, titulo, descricao):
        abort(404)
    return redirect(url_for("index"))


@app.route("/itens/<int:item_id>/excluir", methods=["POST"])
def excluir(item_id):
    if not db.excluir(item_id):
        abort(404)
    return redirect(url_for("index"))


@app.route("/api/itens")
def api_itens():
    return jsonify(
        [
            {
                "id": i["id"],
                "titulo": i["titulo"],
                "descricao": i["descricao"],
                "criado_em": i["criado_em"].isoformat(),
            }
            for i in db.listar()
        ]
    )


@app.route("/healthz")
def healthz():
    """200 com o banco ativo, 503 sem conexão. Usado pelo pipeline e pelo Render."""
    try:
        db.ping()
        return jsonify({"status": "ok"}), 200
    except Exception as exc:  # noqa: BLE001
        app.logger.warning("Health check falhou: %s", exc)
        return jsonify({"status": "erro", "detalhe": "banco indisponível"}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
