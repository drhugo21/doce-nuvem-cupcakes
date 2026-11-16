"""Área administrativa da loja: produtos e pedidos."""
from decimal import Decimal
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .. import db
from ..models import Categoria, Pedido, Produto, StatusPedido
from ..services.order_service import FORMAS_PAGAMENTO, ErroPedido, avancar_status, cancelar_pedido
from ..services.validators import validar_produto

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*a, **kw):
        if not current_user.is_admin:
            abort(403)
        return view(*a, **kw)
    return wrapper


@bp.route("/")
@admin_required
def painel():
    status = request.args.get("status")
    q = Pedido.query
    if status:
        q = q.filter_by(status=status)
    pedidos = q.order_by(Pedido.criado_em.desc()).all()
    return render_template("admin/pedidos.html", pedidos=pedidos, status_atual=status,
                           todos_status=[v for k, v in vars(StatusPedido).items()
                                         if k.isupper() and isinstance(v, str)],
                           formas=FORMAS_PAGAMENTO)


@bp.route("/pedidos/<int:pedido_id>/avancar", methods=["POST"])
@admin_required
def avancar(pedido_id):
    pedido = db.session.get(Pedido, pedido_id) or abort(404)
    try:
        flash(f"Pedido #{pedido.id}: {avancar_status(pedido)}.", "sucesso")
    except ErroPedido as e:
        flash(str(e), "erro")
    return redirect(url_for("admin.painel"))


@bp.route("/pedidos/<int:pedido_id>/cancelar", methods=["POST"])
@admin_required
def cancelar(pedido_id):
    pedido = db.session.get(Pedido, pedido_id) or abort(404)
    try:
        cancelar_pedido(pedido)
        flash(f"Pedido #{pedido.id} cancelado.", "info")
    except ErroPedido as e:
        flash(str(e), "erro")
    return redirect(url_for("admin.painel"))


@bp.route("/produtos")
@admin_required
def produtos():
    return render_template("admin/produtos.html", produtos=Produto.query.order_by(Produto.nome).all())


@bp.route("/produtos/novo", methods=["GET", "POST"])
@bp.route("/produtos/<int:produto_id>", methods=["GET", "POST"])
@admin_required
def produto_form(produto_id=None):
    produto = db.session.get(Produto, produto_id) if produto_id else Produto()
    if produto is None:
        abort(404)
    categorias = Categoria.query.order_by(Categoria.nome).all()
    if request.method == "POST":
        f = request.form
        erros = validar_produto(f)
        if not db.session.get(Categoria, f.get("categoria_id", type=int) or 0):
            erros.append("Escolha uma categoria.")
        if erros:
            for e in erros:
                flash(e, "erro")
            return render_template("admin/produto_form.html", produto=produto,
                                   categorias=categorias, form=f), 400
        produto.nome = f["nome"].strip()
        produto.descricao = f.get("descricao", "").strip()
        produto.preco = Decimal(f["preco"].replace(",", "."))
        produto.estoque = int(f["estoque"])
        produto.cor = f.get("cor", "#f8bbd0")
        produto.categoria_id = int(f["categoria_id"])
        produto.ativo = bool(f.get("ativo"))
        db.session.add(produto)
        db.session.commit()
        flash("Produto salvo.", "sucesso")
        return redirect(url_for("admin.produtos"))
    return render_template("admin/produto_form.html", produto=produto, categorias=categorias, form={})
