"""Comando `flask seed`: cria categorias, cupcakes e o usuário administrador."""
import os
from decimal import Decimal

import click

from . import db
from .models import Categoria, Produto, Usuario

CUPCAKES = [
    ("Clássicos", "Red Velvet", "Massa aveludada com cobertura de cream cheese.", "9.90", 30, "#c62828"),
    ("Clássicos", "Chocolate Belga", "Massa de cacau 50% com ganache de chocolate belga.", "10.90", 30, "#5d4037"),
    ("Clássicos", "Baunilha com Morango", "Massa de baunilha e buttercream de morango fresco.", "8.90", 25, "#f48fb1"),
    ("Gourmet", "Pistache Siciliano", "Recheio de creme de pistache e cobertura de pistache.", "14.90", 15, "#9ccc65"),
    ("Gourmet", "Caramelo Salgado", "Massa amanteigada, recheio de caramelo com flor de sal.", "12.90", 20, "#d4a373"),
    ("Gourmet", "Limão Siciliano", "Massa cítrica com merengue maçaricado.", "11.90", 20, "#fff176"),
    ("Veganos", "Cenoura Vegana", "Sem ingredientes de origem animal, cobertura de chocolate 70%.", "11.50", 12, "#ff9800"),
    ("Sem glúten", "Coco Queimado", "Farinha de arroz e amêndoas, cobertura de coco queimado.", "12.50", 10, "#efebe9"),
]


def popular():
    cats = {}
    for nome_cat, *_ in CUPCAKES:
        if nome_cat not in cats:
            cats[nome_cat] = Categoria.query.filter_by(nome=nome_cat).first() or Categoria(nome=nome_cat)
            db.session.add(cats[nome_cat])
    for cat, nome, desc, preco, estoque, cor in CUPCAKES:
        if not Produto.query.filter_by(nome=nome).first():
            db.session.add(Produto(nome=nome, descricao=desc, preco=Decimal(preco),
                                   estoque=estoque, cor=cor, categoria=cats[cat]))
    email = os.environ.get("ADMIN_EMAIL", "admin@cupcakes.local")
    if not Usuario.query.filter_by(email=email).first():
        admin = Usuario(nome="Administrador", email=email, is_admin=True)
        admin.definir_senha(os.environ.get("ADMIN_PASSWORD", "admin123"))
        db.session.add(admin)
    db.session.commit()


def register_cli(app):
    @app.cli.command("seed")
    def seed():
        """Popula o banco com dados iniciais."""
        popular()
        click.echo("Banco populado.")
