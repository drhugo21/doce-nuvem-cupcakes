"""Checkout, pagamento, entrega e acompanhamento de pedidos."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .. import db
from ..models import Endereco, Pedido
from ..services.cart_service import Carrinho
from ..services.order_service import (FORMAS_PAGAMENTO, ErroPedido, calcular_frete,
                                      cancelar_pedido, criar_pedido)
from ..services.validators import validar_endereco

bp = Blueprint("orders", __name__, url_prefix="/pedidos")


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    carrinho = Carrinho()
    if carrinho.vazio():
        flash("Seu carrinho está vazio.", "aviso")
        return redirect(url_for("shop.vitrine"))

    f = request.form
    if request.method == "POST":
        tipo = f.get("tipo_entrega")
        endereco = None
        try:
            if tipo == "entrega":
                if f.get("endereco_id") == "novo":
                    erros = validar_endereco(f)
                    if erros:
                        raise ErroPedido(" ".join(erros))
                    endereco = Endereco(usuario=current_user, cep=f["cep"].strip(),
                                        logradouro=f["logradouro"].strip(), numero=f["numero"].strip(),
                                        complemento=f.get("complemento", "").strip(),
                                        bairro=f["bairro"].strip(), cidade=f["cidade"].strip(),
                                        uf=f["uf"].strip().upper())
                    db.session.add(endereco)
                else:
                    endereco = db.session.get(Endereco, f.get("endereco_id", type=int) or 0)
                    if not endereco or endereco.usuario_id != current_user.id:
                        raise ErroPedido("Escolha um endereço de entrega.")
            cartao = None
            if f.get("forma_pagamento") == "cartao":
                cartao = {"numero": f.get("cartao_numero", ""), "validade": f.get("cartao_validade", ""),
                          "cvv": f.get("cartao_cvv", "")}
            pedido = criar_pedido(current_user, carrinho, tipo, f.get("forma_pagamento"),
                                  endereco=endereco, observacao=f.get("observacao"),
                                  dados_cartao=cartao)
        except ErroPedido as e:
            db.session.rollback()
            flash(str(e), "erro")
        else:
            flash("Pedido realizado com sucesso! 🎉", "sucesso")
            return redirect(url_for("orders.detalhe", pedido_id=pedido.id))

    subtotal = carrinho.subtotal()
    return render_template("orders/checkout.html", itens=carrinho.itens(), subtotal=subtotal,
                           frete_entrega=calcular_frete(subtotal, "entrega"),
                           enderecos=current_user.enderecos, formas=FORMAS_PAGAMENTO, form=f)


def _pedido_do_usuario(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    if pedido.usuario_id != current_user.id and not current_user.is_admin:
        abort(403)
    return pedido


@bp.route("/")
@login_required
def meus_pedidos():
    return render_template("orders/lista.html", pedidos=current_user.pedidos)


@bp.route("/<int:pedido_id>")
@login_required
def detalhe(pedido_id):
    return render_template("orders/detalhe.html", pedido=_pedido_do_usuario(pedido_id),
                           formas=FORMAS_PAGAMENTO)


@bp.route("/<int:pedido_id>/cancelar", methods=["POST"])
@login_required
def cancelar(pedido_id):
    try:
        cancelar_pedido(_pedido_do_usuario(pedido_id))
        flash("Pedido cancelado.", "info")
    except ErroPedido as e:
        flash(str(e), "erro")
    return redirect(url_for("orders.detalhe", pedido_id=pedido_id))
