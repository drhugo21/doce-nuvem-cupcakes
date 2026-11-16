import pytest

from app import create_app, db
from app.models import Usuario
from app.seed import popular


@pytest.fixture
def app():
    app = create_app({"TESTING": True, "CSRF_ENABLED": False, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        db.create_all()
        popular()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def cadastrar(client, email="cliente@teste.com", senha="segredo1"):
    return client.post("/conta/cadastro", data={"nome": "Cliente Teste", "email": email,
                                                "senha": senha, "confirmacao": senha},
                       follow_redirects=True)


def login(client, email, senha):
    return client.post("/conta/login", data={"email": email, "senha": senha}, follow_redirects=True)


@pytest.fixture
def cliente(client):
    cadastrar(client)
    return client


@pytest.fixture
def admin_client(client):
    login(client, "admin@cupcakes.local", "admin123")
    return client


ENDERECO = {"endereco_id": "novo", "cep": "01001-000", "logradouro": "Praça da Sé",
            "numero": "100", "bairro": "Sé", "cidade": "São Paulo", "uf": "SP"}
CARTAO_OK = {"cartao_numero": "4111 1111 1111 1111", "cartao_validade": "12/39", "cartao_cvv": "123"}
