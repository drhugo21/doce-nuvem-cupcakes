"""Camada Model: entidades persistidas no PostgreSQL."""
from datetime import datetime, timezone
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


def agora():
    return datetime.now(timezone.utc)


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    telefone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), default=agora)

    enderecos = db.relationship("Endereco", backref="usuario", cascade="all, delete-orphan")
    pedidos = db.relationship("Pedido", backref="usuario", order_by="Pedido.criado_em.desc()")

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


@login_manager.user_loader
def carregar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))


class Categoria(db.Model):
    __tablename__ = "categorias"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(60), unique=True, nullable=False)
    produtos = db.relationship("Produto", backref="categoria")


class Produto(db.Model):
    __tablename__ = "produtos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=False, default="")
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)
    cor = db.Column(db.String(7), nullable=False, default="#f8bbd0")
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)

    __table_args__ = (
        db.CheckConstraint("preco > 0", name="ck_produto_preco_positivo"),
        db.CheckConstraint("estoque >= 0", name="ck_produto_estoque_nao_negativo"),
    )

    @property
    def disponivel(self):
        return self.ativo and self.estoque > 0


class Endereco(db.Model):
    __tablename__ = "enderecos"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    logradouro = db.Column(db.String(160), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    complemento = db.Column(db.String(60))
    bairro = db.Column(db.String(80), nullable=False)
    cidade = db.Column(db.String(80), nullable=False)
    uf = db.Column(db.String(2), nullable=False)

    def formatado(self):
        comp = f", {self.complemento}" if self.complemento else ""
        return (f"{self.logradouro}, {self.numero}{comp} - {self.bairro}, "
                f"{self.cidade}/{self.uf} - CEP {self.cep}")


class StatusPedido:
    AGUARDANDO_PAGAMENTO = "Aguardando pagamento"
    PAGO = "Pago"
    EM_PREPARO = "Em preparo"
    SAIU_PARA_ENTREGA = "Saiu para entrega"
    PRONTO_RETIRADA = "Pronto para retirada"
    ENTREGUE = "Entregue"
    CANCELADO = "Cancelado"

    FLUXO_ENTREGA = [AGUARDANDO_PAGAMENTO, PAGO, EM_PREPARO, SAIU_PARA_ENTREGA, ENTREGUE]
    FLUXO_RETIRADA = [AGUARDANDO_PAGAMENTO, PAGO, EM_PREPARO, PRONTO_RETIRADA, ENTREGUE]
    CANCELAVEIS = {AGUARDANDO_PAGAMENTO, PAGO}


class Pedido(db.Model):
    __tablename__ = "pedidos"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default=StatusPedido.AGUARDANDO_PAGAMENTO)
    tipo_entrega = db.Column(db.String(10), nullable=False)  # "entrega" | "retirada"
    endereco_entrega = db.Column(db.String(300))
    forma_pagamento = db.Column(db.String(20), nullable=False)  # pix | cartao | dinheiro
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    frete = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total = db.Column(db.Numeric(10, 2), nullable=False)
    observacao = db.Column(db.String(300))
    criado_em = db.Column(db.DateTime(timezone=True), default=agora, nullable=False)

    itens = db.relationship("ItemPedido", backref="pedido", cascade="all, delete-orphan")

    @property
    def fluxo(self):
        return (StatusPedido.FLUXO_ENTREGA if self.tipo_entrega == "entrega"
                else StatusPedido.FLUXO_RETIRADA)

    @property
    def pode_cancelar(self):
        return self.status in StatusPedido.CANCELAVEIS

    def proximo_status(self):
        if self.status not in self.fluxo:
            return None
        i = self.fluxo.index(self.status)
        return self.fluxo[i + 1] if i + 1 < len(self.fluxo) else None


class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    produto = db.relationship("Produto")

    __table_args__ = (db.CheckConstraint("quantidade > 0", name="ck_item_qtd_positiva"),)

    @property
    def subtotal(self):
        return self.preco_unitario * self.quantidade
