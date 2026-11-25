import logging
from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
import db

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

@app.before_request
def preparar_banco():
    if request.path != "/healthz":
        db.ensure_schema()

@app.route("/")
def index():
    return render_template("index.html", itens=db.listar())

@app.route("/itens", methods=["POST"])
def criar():
    titulo = request.form.get("titulo", "").strip()
    ano = request.form.get("ano", "").strip()
    genero = request.form.get("genero", "").strip()
    assistido = request.form.get("assistido", "").strip()
    
    if not titulo or not ano or not genero or not assistido:
        abort(400, "Todos os campos são obrigatórios.")
    
    db.criar(titulo, int(ano), genero, assistido)
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
    ano = request.form.get("ano", "").strip()
    genero = request.form.get("genero", "").strip()
    assistido = request.form.get("assistido", "").strip()
    
    if not titulo or not ano or not genero or not assistido:
        abort(400, "Todos os campos são obrigatórios.")
    
    if not db.atualizar(item_id, titulo, int(ano), genero, assistido):
        abort(404)
    return redirect(url_for("index"))

@app.route("/itens/<int:item_id>/excluir", methods=["POST"])
def excluir(item_id):
    if not db.excluir(item_id):
        abort(404)
    return redirect(url_for("index"))

@app.route("/healthz")
def healthz():
    try:
        db.ping()
        return jsonify({"status": "ok"}), 200
    except Exception as exc:
        app.logger.warning("Health check falhou: %s", exc)
        return jsonify({"status": "erro", "detalhe": "banco indisponível"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
