"""Cadastro, login e logout de clientes."""
from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .. import db
from ..models import Usuario
from ..services.validators import validar_cadastro

bp = Blueprint("auth", __name__, url_prefix="/conta")


def _destino_seguro(url):
    return url if url and not urlparse(url).netloc and url.startswith("/") else None


@bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for("shop.vitrine"))
    if request.method == "POST":
        f = request.form
        email = f.get("email", "").strip().lower()
        erros = validar_cadastro(f.get("nome"), email, f.get("senha"), f.get("confirmacao"))
        if not erros and Usuario.query.filter_by(email=email).first():
            erros.append("Já existe uma conta com este e-mail.")
        if erros:
            for e in erros:
                flash(e, "erro")
            return render_template("auth/cadastro.html", form=f), 400
        u = Usuario(nome=f["nome"].strip(), email=email, telefone=f.get("telefone", "").strip())
        u.definir_senha(f["senha"])
        db.session.add(u)
        db.session.commit()
        login_user(u)
        flash(f"Bem-vindo(a), {u.nome.split()[0]}! 🧁", "sucesso")
        return redirect(url_for("shop.vitrine"))
    return render_template("auth/cadastro.html", form={})


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("shop.vitrine"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        u = Usuario.query.filter_by(email=email).first()
        if not u or not u.verificar_senha(request.form.get("senha", "")):
            flash("E-mail ou senha incorretos.", "erro")
            return render_template("auth/login.html", email=email), 401
        login_user(u, remember=bool(request.form.get("lembrar")))
        return redirect(_destino_seguro(request.args.get("next")) or url_for("shop.vitrine"))
    return render_template("auth/login.html", email="")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("shop.vitrine"))
