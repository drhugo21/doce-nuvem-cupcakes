"""Carrinho de compras."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..services.cart_service import Carrinho, ErroCarrinho
from ..services.order_service import FRETE_GRATIS_A_PARTIR, PEDIDO_MINIMO

bp = Blueprint("cart", __name__, url_prefix="/carrinho")


@bp.route("/")
def ver():
    c = Carrinho()
    return render_template("cart/carrinho.html", itens=c.itens(), subtotal=c.subtotal(),
                           frete_gratis=FRETE_GRATIS_A_PARTIR, minimo=PEDIDO_MINIMO)


@bp.route("/adicionar/<int:produto_id>", methods=["POST"])
def adicionar(produto_id):
    qtd = request.form.get("quantidade", 1, type=int) or 0
    try:
        p = Carrinho().adicionar(produto_id, qtd)
        flash(f"{p.nome} adicionado ao carrinho.", "sucesso")
    except ErroCarrinho as e:
        flash(str(e), "erro")
    return redirect(request.form.get("voltar") or url_for("cart.ver"))


@bp.route("/atualizar/<int:produto_id>", methods=["POST"])
def atualizar(produto_id):
    try:
        Carrinho().atualizar(produto_id, request.form.get("quantidade", 0, type=int) or 0)
    except ErroCarrinho as e:
        flash(str(e), "erro")
    return redirect(url_for("cart.ver"))


@bp.route("/remover/<int:produto_id>", methods=["POST"])
def remover(produto_id):
    Carrinho().remover(produto_id)
    flash("Item removido.", "info")
    return redirect(url_for("cart.ver"))
