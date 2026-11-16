"""Testes de integração: rotas, banco e sessão funcionando juntos."""
from app import db
from app.models import Pedido, Produto, StatusPedido

from .conftest import CARTAO_OK, ENDERECO, cadastrar, login


def produto(nome):
    return Produto.query.filter_by(nome=nome).one()


# ---------- Vitrine ----------
def test_vitrine_lista_produtos(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Red Velvet" in r.text and "Pistache Siciliano" in r.text


def test_vitrine_busca_e_filtro(client):
    r = client.get("/?q=pistache")
    assert "Pistache" in r.text and "Red Velvet" not in r.text


def test_produto_inexistente_404(client):
    assert client.get("/produto/9999").status_code == 404


def test_produto_inativo_nao_aparece(client):
    p = produto("Red Velvet"); p.ativo = False; db.session.commit()
    assert "Red Velvet" not in client.get("/").text
    assert client.get(f"/produto/{p.id}").status_code == 404


# ---------- Conta ----------
def test_cadastro_e_login(client):
    r = cadastrar(client)
    assert "Bem-vindo" in r.text
    client.post("/conta/logout")
    assert "Meus pedidos" in login(client, "cliente@teste.com", "segredo1").text


def test_cadastro_email_duplicado(client):
    cadastrar(client); client.post("/conta/logout")
    r = cadastrar(client)
    assert r.status_code == 400 and "Já existe" in r.text


def test_login_senha_errada(client):
    cadastrar(client); client.post("/conta/logout")
    r = login(client, "cliente@teste.com", "errada")
    assert r.status_code == 401 and "incorretos" in r.text


def test_login_nao_redireciona_para_site_externo(client):
    cadastrar(client); client.post("/conta/logout")
    r = client.post("/conta/login?next=https://malicioso.com",
                    data={"email": "cliente@teste.com", "senha": "segredo1"})
    assert "malicioso" not in r.headers["Location"]


# ---------- Carrinho ----------
def test_adicionar_e_remover_do_carrinho(client):
    p = produto("Red Velvet")
    client.post(f"/carrinho/adicionar/{p.id}", data={"quantidade": 2})
    r = client.get("/carrinho/")
    assert "Red Velvet" in r.text and "19,80" in r.text
    client.post(f"/carrinho/remover/{p.id}")
    assert "vazio" in client.get("/carrinho/").text


def test_carrinho_nao_passa_do_estoque(client):
    p = produto("Coco Queimado")  # estoque 10
    r = client.post(f"/carrinho/adicionar/{p.id}", data={"quantidade": 11}, follow_redirects=True)
    assert "Só temos 10" in r.text


def test_carrinho_quantidade_invalida(client):
    p = produto("Red Velvet")
    r = client.post(f"/carrinho/adicionar/{p.id}", data={"quantidade": -3}, follow_redirects=True)
    assert "Quantidade inválida" in r.text


# ---------- Checkout / pagamento / entrega ----------
def test_checkout_exige_login(client):
    r = client.get("/pedidos/checkout")
    assert r.status_code == 302 and "/conta/login" in r.headers["Location"]


def test_pedido_pix_com_entrega(cliente):
    p = produto("Red Velvet")
    cliente.post(f"/carrinho/adicionar/{p.id}", data={"quantidade": 3})
    r = cliente.post("/pedidos/checkout", data={"tipo_entrega": "entrega", "forma_pagamento": "pix",
                                                **ENDERECO}, follow_redirects=True)
    assert "Pedido realizado" in r.text
    pedido = Pedido.query.one()
    assert pedido.status == StatusPedido.PAGO
    assert str(pedido.total) == "37.70"  # 29,70 + 8,00 de frete
    assert "Praça da Sé" in pedido.endereco_entrega
    assert produto("Red Velvet").estoque == 27
    assert "Seu carrinho está vazio" in cliente.get("/carrinho/").text


def test_frete_gratis_acima_de_100(cliente):
    p = produto("Pistache Siciliano")
    cliente.post(f"/carrinho/adicionar/{p.id}", data={"quantidade": 7})  # 104,30
    cliente.post("/pedidos/checkout", data={"tipo_entrega": "entrega", "forma_pagamento": "pix", **ENDERECO})
    assert Pedido.query.one().frete == 0


def test_pedido_cartao_valido(cliente):
    cliente.post(f"/carrinho/adicionar/{produto('Red Velvet').id}", data={"quantidade": 2})
    cliente.post("/pedidos/checkout", data={"tipo_entrega": "retirada", "forma_pagamento": "cartao", **CARTAO_OK})
    assert Pedido.query.one().status == StatusPedido.PAGO


def test_pedido_cartao_invalido_nao_cria_pedido(cliente):
    p = produto("Red Velvet")
    cliente.post(f"/carrinho/adicionar/{p.id}", data={"quantidade": 2})
    r = cliente.post("/pedidos/checkout", data={"tipo_entrega": "retirada", "forma_pagamento": "cartao",
                                                **CARTAO_OK, "cartao_numero": "4111111111111112"})
    assert "Número do cartão inválido" in r.text
    assert Pedido.query.count() == 0
    assert produto("Red Velvet").estoque == 30


def test_pedido_dinheiro_fica_aguardando(cliente):
    cliente.post(f"/carrinho/adicionar/{produto('Red Velvet').id}", data={"quantidade": 2})
    cliente.post("/pedidos/checkout", data={"tipo_entrega": "retirada", "forma_pagamento": "dinheiro"})
    assert Pedido.query.one().status == StatusPedido.AGUARDANDO_PAGAMENTO


def test_pedido_minimo(cliente):
    cliente.post(f"/carrinho/adicionar/{produto('Red Velvet').id}", data={"quantidade": 1})
    r = cliente.post("/pedidos/checkout", data={"tipo_entrega": "retirada", "forma_pagamento": "pix"})
    assert "pedido mínimo" in r.text and Pedido.query.count() == 0


def test_endereco_invalido(cliente):
    cliente.post(f"/carrinho/adicionar/{produto('Red Velvet').id}", data={"quantidade": 2})
    r = cliente.post("/pedidos/checkout", data={"tipo_entrega": "entrega", "forma_pagamento": "pix",
                                                **ENDERECO, "cep": "abc"})
    assert "CEP inválido" in r.text and Pedido.query.count() == 0


def test_estoque_acabou_entre_carrinho_e_checkout(cliente):
    p = produto("Coco Queimado")
    cliente.post(f"/carrinho/adicionar/{p.id}", data={"quantidade": 5})
    p.estoque = 2; db.session.commit()
    r = cliente.post("/pedidos/checkout", data={"tipo_entrega": "retirada", "forma_pagamento": "pix"})
    assert "apenas 2" in r.text and Pedido.query.count() == 0


# ---------- Acompanhamento e cancelamento ----------
def _fazer_pedido(c, forma="pix"):
    c.post(f"/carrinho/adicionar/{produto('Red Velvet').id}", data={"quantidade": 2})
    c.post("/pedidos/checkout", data={"tipo_entrega": "retirada", "forma_pagamento": forma})
    return Pedido.query.order_by(Pedido.id.desc()).first()


def test_cliente_cancela_e_estoque_volta(cliente):
    pedido = _fazer_pedido(cliente)
    cliente.post(f"/pedidos/{pedido.id}/cancelar")
    assert db.session.get(Pedido, pedido.id).status == StatusPedido.CANCELADO
    assert produto("Red Velvet").estoque == 30


def test_nao_cancela_em_preparo(cliente):
    pedido = _fazer_pedido(cliente)
    pedido.status = StatusPedido.EM_PREPARO; db.session.commit()
    r = cliente.post(f"/pedidos/{pedido.id}/cancelar", follow_redirects=True)
    assert "não pode mais ser cancelado" in r.text


def test_cliente_nao_ve_pedido_de_outro(client):
    cadastrar(client, "a@teste.com"); pedido = _fazer_pedido(client); client.post("/conta/logout")
    cadastrar(client, "b@teste.com")
    assert client.get(f"/pedidos/{pedido.id}").status_code == 403


# ---------- Administração ----------
def test_cliente_nao_acessa_admin(cliente):
    assert cliente.get("/admin/").status_code == 403


def test_admin_avanca_status_ate_entregue(client):
    cadastrar(client); pedido = _fazer_pedido(client); client.post("/conta/logout")
    login(client, "admin@cupcakes.local", "admin123")
    for esperado in [StatusPedido.EM_PREPARO, StatusPedido.PRONTO_RETIRADA, StatusPedido.ENTREGUE]:
        client.post(f"/admin/pedidos/{pedido.id}/avancar")
        assert db.session.get(Pedido, pedido.id).status == esperado
    r = client.post(f"/admin/pedidos/{pedido.id}/avancar", follow_redirects=True)
    assert "não pode avançar" in r.text


def test_admin_cria_produto(admin_client):
    r = admin_client.post("/admin/produtos/novo", data={"nome": "Nutella", "descricao": "Avelã",
                          "preco": "13,90", "estoque": "8", "cor": "#6d4c41", "categoria_id": 2,
                          "ativo": "on"}, follow_redirects=True)
    assert "Produto salvo" in r.text
    assert str(produto("Nutella").preco) == "13.90"


def test_admin_produto_invalido(admin_client):
    r = admin_client.post("/admin/produtos/novo", data={"nome": "X", "preco": "0", "estoque": "-1",
                                                        "categoria_id": 1})
    assert r.status_code == 400 and "Preço deve ser maior" in r.text
