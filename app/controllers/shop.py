"""Vitrine virtual."""
from flask import Blueprint, abort, render_template, request

from .. import db
from ..models import Categoria, Produto

bp = Blueprint("shop", __name__)


@bp.route("/")
def vitrine():
    categoria_id = request.args.get("categoria", type=int)
    busca = request.args.get("q", "").strip()
    consulta = Produto.query.filter_by(ativo=True)
    if categoria_id:
        consulta = consulta.filter_by(categoria_id=categoria_id)
    if busca:
        consulta = consulta.filter(Produto.nome.ilike(f"%{busca}%"))
    produtos = consulta.order_by(Produto.nome).all()
    categorias = Categoria.query.order_by(Categoria.nome).all()
    return render_template("shop/vitrine.html", produtos=produtos, categorias=categorias,
                           categoria_id=categoria_id, busca=busca)


@bp.route("/produto/<int:produto_id>")
def detalhe(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto or not produto.ativo:
        abort(404)
    return render_template("shop/detalhe.html", produto=produto)
