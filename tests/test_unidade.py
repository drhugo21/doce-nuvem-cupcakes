"""Testes de unidade das regras de negócio (services)."""
from datetime import date
from decimal import Decimal

import pytest

from app.models import Pedido, StatusPedido
from app.services.order_service import (ErroPedido, calcular_frete, luhn_valido,
                                        validar_cartao)
from app.services.validators import validar_cadastro, validar_endereco, validar_produto


@pytest.mark.parametrize("subtotal,tipo,esperado", [
    ("50.00", "entrega", "8.00"),
    ("99.99", "entrega", "8.00"),
    ("100.00", "entrega", "0.00"),
    ("20.00", "retirada", "0.00"),
])
def test_calcular_frete(subtotal, tipo, esperado):
    assert calcular_frete(Decimal(subtotal), tipo) == Decimal(esperado)


def test_luhn():
    assert luhn_valido("4111111111111111")
    assert luhn_valido("5555 5555 5555 4444")
    assert not luhn_valido("4111111111111112")
    assert not luhn_valido("123")


def test_cartao_vencido():
    with pytest.raises(ErroPedido, match="vencido"):
        validar_cartao("4111111111111111", "01/20", "123", hoje=date(2026, 11, 15))


def test_cartao_validade_mal_formatada():
    with pytest.raises(ErroPedido, match="MM/AA"):
        validar_cartao("4111111111111111", "13/30", "123")


def test_cartao_cvv_invalido():
    with pytest.raises(ErroPedido, match="CVV"):
        validar_cartao("4111111111111111", "12/39", "12")


def test_validar_cadastro():
    assert validar_cadastro("Maria Silva", "maria@x.com", "123456", "123456") == []
    erros = validar_cadastro("M", "invalido", "123", "456")
    assert len(erros) == 4


def test_validar_endereco():
    ok = {"cep": "01001-000", "logradouro": "Rua A", "numero": "1", "bairro": "B",
          "cidade": "C", "uf": "sp"}
    assert validar_endereco(ok) == []
    assert "UF inválida." in validar_endereco({**ok, "uf": "XX"})
    assert any("CEP" in e for e in validar_endereco({**ok, "cep": "123"}))


def test_validar_produto():
    assert validar_produto({"nome": "Teste", "preco": "9,90", "estoque": "3", "cor": "#ffffff"}) == []
    assert len(validar_produto({"nome": "T", "preco": "-1", "estoque": "x", "cor": "rosa"})) == 4


def test_fluxo_status():
    p = Pedido(tipo_entrega="entrega", status=StatusPedido.PAGO)
    assert p.proximo_status() == StatusPedido.EM_PREPARO
    p.status = StatusPedido.ENTREGUE
    assert p.proximo_status() is None
    r = Pedido(tipo_entrega="retirada", status=StatusPedido.EM_PREPARO)
    assert r.proximo_status() == StatusPedido.PRONTO_RETIRADA


def test_url_do_banco_usa_psycopg2(monkeypatch):
    from app import _database_url
    for url in ("postgres://u:s@h/db", "postgresql://u:s@h/db"):
        monkeypatch.setenv("DATABASE_URL", url)
        assert _database_url() == "postgresql+psycopg2://u:s@h/db"
