# 🧁 Doce Nuvem — Loja virtual de cupcakes gourmet

Projeto Integrador Transdisciplinar em Engenharia de Software II (Cruzeiro do Sul).
Continuação da PIT I: app de vitrine virtual, pedido eletrônico, pagamento e entrega.

| Item | Escolha |
|---|---|
| Back-end | Python 3 + Flask (padrão **MVC**) |
| Banco de dados | PostgreSQL (SQLite só no desenvolvimento local e nos testes) |
| Front-end | HTML, CSS e JavaScript (templates Jinja2), responsivo |
| Testes | pytest: 39 testes de unidade e de integração |
| Hospedagem | Render (web service + PostgreSQL gratuitos) |
| Modo de codificação | Tradicional |

## Funcionalidades
- **Vitrine:** listagem, busca por nome, filtro por categoria, página do produto, aviso de esgotado.
- **Conta:** cadastro, login e logout, senha com hash.
- **Carrinho:** adicionar, alterar quantidade e remover itens; respeita o estoque; mostra quanto falta para o frete grátis.
- **Pedido:** entrega em casa (R$ 8,00, grátis a partir de R$ 100) ou retirada na loja; pedido mínimo de R$ 15.
- **Pagamento (simulado):** PIX, cartão de crédito (validação de número pelo algoritmo de Luhn, validade e CVV; nada é armazenado) ou dinheiro na entrega.
- **Acompanhamento:** linha do tempo do status; o cliente cancela enquanto o pedido não estiver em preparo, e o estoque é devolvido.
- **Admin:** painel de pedidos com filtro e avanço de status; cadastro e edição de produtos.
- **Tratamento de erros:** validação em todos os formulários e páginas próprias para os erros 403, 404 e 500.

## Estrutura (MVC)
```
app/
  models.py          # Model: Usuario, Categoria, Produto, Endereco, Pedido, ItemPedido
  controllers/       # Controller: shop, auth, cart, orders, admin (Blueprints)
  services/          # Regras de negócio: carrinho, pedido/frete/pagamento, validações
  templates/         # View: HTML (Jinja2)
  static/css/        # Estilos
  seed.py            # comando `flask seed`
tests/               # pytest: unidade e integração
```

## Rodar localmente
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/flask --app run seed
.venv/bin/flask --app run run
```
Acesse http://localhost:5000. Login de administrador de teste: `admin@cupcakes.local` / `admin123`
(em produção defina `ADMIN_EMAIL` e `ADMIN_PASSWORD`).

Para usar PostgreSQL localmente, defina antes de rodar:
`export DATABASE_URL=postgresql://usuario:senha@localhost:5432/cupcakes`

## Testes
```bash
.venv/bin/python -m pytest -v
```

## Deploy no Render
1. Suba o projeto para o GitHub.
2. No Render, escolha **New → Blueprint** e selecione o repositório. O `render.yaml` cria o banco PostgreSQL e o serviço web.
3. Informe `ADMIN_PASSWORD` quando o Render pedir.
