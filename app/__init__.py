"""Fábrica da aplicação Flask (padrão MVC).

Model      -> app/models.py
View       -> app/templates/
Controller -> app/controllers/
Regras de negócio isoladas em app/services/.
"""
import os
import secrets
from datetime import timezone
from zoneinfo import ZoneInfo

from flask import Flask, abort, render_template, request, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para continuar."
login_manager.login_message_category = "aviso"


def _database_url():
    url = os.environ.get("DATABASE_URL", "sqlite:///cupcakes.db")
    # Render entrega "postgres://" ou "postgresql://". O SQLAlchemy 2.1 usa o driver
    # psycopg (v3) por padrão; aqui fixamos o psycopg2, que é o instalado.
    for prefixo in ("postgres://", "postgresql://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg2://" + url[len(prefixo):]
    return url


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-troque-em-producao"),
        SQLALCHEMY_DATABASE_URI=_database_url(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CSRF_ENABLED=True,
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    login_manager.init_app(app)

    from .controllers import admin, auth, cart, orders, shop
    for bp in (shop.bp, auth.bp, cart.bp, orders.bp, admin.bp):
        app.register_blueprint(bp)

    from .services.cart_service import Carrinho

    @app.context_processor
    def inject_cart():
        return {"qtd_carrinho": Carrinho().quantidade_total()}

    # Proteção CSRF: todo POST precisa do token gerado na sessão
    def csrf_token():
        if "_csrf" not in session:
            session["_csrf"] = secrets.token_urlsafe(32)
        return session["_csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def verificar_csrf():
        if request.method == "POST" and app.config["CSRF_ENABLED"]:
            enviado = request.form.get("_csrf", "")
            if not enviado or not secrets.compare_digest(enviado, session.get("_csrf", "")):
                abort(400)

    # Datas são gravadas em UTC e exibidas no horário de Brasília
    fuso = ZoneInfo("America/Sao_Paulo")

    @app.template_filter("data_local")
    def data_local(valor, formato="%d/%m/%Y %H:%M"):
        if valor.tzinfo is None:
            valor = valor.replace(tzinfo=timezone.utc)
        return valor.astimezone(fuso).strftime(formato)

    @app.errorhandler(400)
    def requisicao_invalida(e):
        return render_template("erro.html", codigo=400,
                               mensagem="Sua sessão expirou ou a requisição é inválida. Recarregue a página e tente de novo."), 400

    @app.errorhandler(404)
    def nao_encontrado(e):
        return render_template("erro.html", codigo=404,
                               mensagem="Página não encontrada."), 404

    @app.errorhandler(403)
    def proibido(e):
        return render_template("erro.html", codigo=403,
                               mensagem="Você não tem permissão para acessar esta página."), 403

    @app.errorhandler(500)
    def erro_interno(e):
        db.session.rollback()
        return render_template("erro.html", codigo=500,
                               mensagem="Ops! Algo deu errado. Tente novamente."), 500

    from .seed import register_cli
    register_cli(app)

    with app.app_context():
        db.create_all()

    return app
