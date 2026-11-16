"""Testes de regressão das correções apontadas no laudo de qualidade."""
from datetime import datetime, timezone

from app import create_app, db
from app.seed import popular

from .conftest import cadastrar


def test_c01_carrinho_nao_redireciona_para_site_externo(client):
    for destino in ["https://site-malicioso.com", "//site-malicioso.com"]:
        r = client.post("/carrinho/adicionar/1", data={"quantidade": 1, "voltar": destino})
        assert "malicioso" not in r.headers["Location"]
    r = client.post("/carrinho/adicionar/1", data={"quantidade": 1, "voltar": "/?q=red"})
    assert r.headers["Location"] == "/?q=red"


def test_c02_logout_por_get_nao_e_permitido(client):
    cadastrar(client)
    assert client.get("/conta/logout").status_code == 405


def test_c03_csrf_bloqueia_post_sem_token():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all(); popular()
        c = app.test_client()
        assert c.post("/carrinho/adicionar/1", data={"quantidade": 1}).status_code == 400
        c.get("/")  # gera o token na sessão
        with c.session_transaction() as s:
            token = s["_csrf"]
        r = c.post("/carrinho/adicionar/1", data={"quantidade": 1, "_csrf": token})
        assert r.status_code == 302
        db.drop_all()


def test_c04_telefone_invalido_rejeitado(client):
    r = client.post("/conta/cadastro", data={"nome": "Teste Tel", "email": "t@x.com", "telefone": "abcxyz",
                                             "senha": "123456", "confirmacao": "123456"})
    assert r.status_code == 400 and "Telefone inválido" in r.text
    r = client.post("/conta/cadastro", data={"nome": "Teste Tel", "email": "t@x.com", "telefone": "(11) 91234-5678",
                                             "senha": "123456", "confirmacao": "123456"})
    assert r.status_code == 302


def test_c05_horario_exibido_em_brasilia(app):
    filtro = app.jinja_env.filters["data_local"]
    utc = datetime(2026, 11, 16, 0, 30, tzinfo=timezone.utc)
    assert filtro(utc) == "15/11/2026 21:30"
    assert filtro(utc.replace(tzinfo=None)) == "15/11/2026 21:30"  # SQLite devolve sem fuso
