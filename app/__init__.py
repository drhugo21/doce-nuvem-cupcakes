"""Fábrica da aplicação Flask (padrão MVC).

Model      -> app/models.py
View       -> app/templates/
Controller -> app/controllers/
Regras de negócio isoladas em app/services/.
"""
import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para continuar."
login_manager.login_message_category = "aviso"


def _database_url():
    url = os.environ.get("DATABASE_URL", "sqlite:///cupcakes.db")
    # Render/Heroku entregam "postgres://", o SQLAlchemy exige "postgresql://"
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-troque-em-producao"),
        SQLALCHEMY_DATABASE_URI=_database_url(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
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
