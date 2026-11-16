"""Regras de negócio de pedido, frete e pagamento."""
import re
from datetime import date
from decimal import Decimal

from .. import db
from ..models import ItemPedido, Pedido, Produto, StatusPedido

TAXA_ENTREGA = Decimal("8.00")
FRETE_GRATIS_A_PARTIR = Decimal("100.00")
PEDIDO_MINIMO = Decimal("15.00")
FORMAS_PAGAMENTO = {"pix": "PIX", "cartao": "Cartão de crédito", "dinheiro": "Dinheiro na entrega"}


class ErroPedido(Exception):
    pass


def calcular_frete(subtotal, tipo_entrega):
    if tipo_entrega == "retirada" or subtotal >= FRETE_GRATIS_A_PARTIR:
        return Decimal("0.00")
    return TAXA_ENTREGA


def luhn_valido(numero):
    digitos = [int(d) for d in re.sub(r"\D", "", numero)]
    if not 13 <= len(digitos) <= 19:
        return False
    soma = 0
    for i, d in enumerate(reversed(digitos)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        soma += d
    return soma % 10 == 0


def validar_cartao(numero, validade, cvv, hoje=None):
    """Valida os dados do cartão. Nada é armazenado: o pagamento é simulado."""
    hoje = hoje or date.today()
    if not luhn_valido(numero or ""):
        raise ErroPedido("Número do cartão inválido.")
    m = re.fullmatch(r"(\d{2})/(\d{2})", (validade or "").strip())
    if not m or not 1 <= int(m.group(1)) <= 12:
        raise ErroPedido("Validade deve estar no formato MM/AA.")
    mes, ano = int(m.group(1)), 2000 + int(m.group(2))
    if (ano, mes) < (hoje.year, hoje.month):
        raise ErroPedido("Cartão vencido.")
    if not re.fullmatch(r"\d{3,4}", (cvv or "").strip()):
        raise ErroPedido("CVV inválido.")


def criar_pedido(usuario, carrinho, tipo_entrega, forma_pagamento,
                 endereco=None, observacao=None, dados_cartao=None):
    itens = carrinho.itens()
    if not itens:
        raise ErroPedido("Seu carrinho está vazio.")
    if tipo_entrega not in ("entrega", "retirada"):
        raise ErroPedido("Escolha entrega ou retirada.")
    if forma_pagamento not in FORMAS_PAGAMENTO:
        raise ErroPedido("Escolha uma forma de pagamento.")
    if tipo_entrega == "entrega" and endereco is None:
        raise ErroPedido("Informe um endereço de entrega.")

    subtotal = sum((s for _, _, s in itens), Decimal("0.00"))
    if subtotal < PEDIDO_MINIMO:
        raise ErroPedido(f"O pedido mínimo é de R$ {PEDIDO_MINIMO:.2f}.".replace(".", ","))

    if forma_pagamento == "cartao":
        validar_cartao(**(dados_cartao or {}))

    # Confere e baixa estoque com bloqueio de linha (evita vender o mesmo cupcake duas vezes)
    for produto, qtd, _ in itens:
        p = db.session.query(Produto).filter_by(id=produto.id).with_for_update().one()
        if qtd > p.estoque:
            db.session.rollback()
            raise ErroPedido(f"{p.nome} tem apenas {p.estoque} unidade(s) em estoque.")
        p.estoque -= qtd

    frete = calcular_frete(subtotal, tipo_entrega)
    pedido = Pedido(
        usuario=usuario,
        tipo_entrega=tipo_entrega,
        endereco_entrega=endereco.formatado() if endereco and tipo_entrega == "entrega" else None,
        forma_pagamento=forma_pagamento,
        subtotal=subtotal,
        frete=frete,
        total=subtotal + frete,
        observacao=(observacao or "").strip()[:300] or None,
    )
    # PIX e cartão são aprovados na hora (simulação); dinheiro fica aguardando
    if forma_pagamento in ("pix", "cartao"):
        pedido.status = StatusPedido.PAGO
    for produto, qtd, _ in itens:
        pedido.itens.append(ItemPedido(produto_id=produto.id, quantidade=qtd,
                                       preco_unitario=produto.preco))
    db.session.add(pedido)
    db.session.commit()
    carrinho.limpar()
    return pedido


def cancelar_pedido(pedido):
    if not pedido.pode_cancelar:
        raise ErroPedido("Este pedido já está em preparo e não pode mais ser cancelado.")
    for item in pedido.itens:
        item.produto.estoque += item.quantidade
    pedido.status = StatusPedido.CANCELADO
    db.session.commit()


def avancar_status(pedido):
    proximo = pedido.proximo_status()
    if not proximo:
        raise ErroPedido("Este pedido não pode avançar de status.")
    pedido.status = proximo
    db.session.commit()
    return proximo
