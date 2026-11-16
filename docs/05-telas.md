# 5. Telas (IHC)

Capturas do sistema em funcionamento. As telas seguem o protótipo da PIT I, com estas melhorias:
- **Paleta:** rosa e creme, para identidade de confeitaria.
- **Ilustração:** cada cupcake é desenhado na cor da sua cobertura, sem depender de fotos.
- **Mensagens:** erros e confirmações aparecem no topo, em português.
- **Andamento do pedido:** linha do tempo do status.
- **Celular:** layout que se adapta à tela.

## Mapa navegacional

```mermaid
flowchart TD
    V[Vitrine] --> D[Detalhe do produto]
    V --> C[Carrinho]
    D --> C
    V --> L[Login]
    L --> CAD[Cadastro]
    C --> CK[Checkout: entrega + pagamento]
    CK -->|não logado| L
    CK --> P[Pedido / acompanhamento]
    V --> MP[Meus pedidos] --> P
    V --> ADM[Painel admin: pedidos]
    ADM --> PR[Produtos] --> PF[Novo/editar produto]
```

## Mensagens de erro principais
| Situação | Mensagem |
|---|---|
| Login inválido | "E-mail ou senha incorretos." |
| E-mail já cadastrado | "Já existe uma conta com este e-mail." |
| Acima do estoque | "Só temos N unidade(s) de X em estoque." |
| Pedido abaixo do mínimo | "O pedido mínimo é de R$ 15,00." |
| Cartão inválido / vencido | "Número do cartão inválido." / "Cartão vencido." |
| CEP inválido | "CEP inválido (use 00000-000)." |
| Cancelar pedido em preparo | "Este pedido já está em preparo e não pode mais ser cancelado." |
| Página inexistente / sem permissão | Páginas 404 e 403 com link para voltar à vitrine |

## Capturas
| Tela | Imagem |
|---|---|
| Vitrine | ![](telas/01-vitrine.png) |
| Detalhe do produto | ![](telas/02-detalhe-produto.png) |
| Cadastro | ![](telas/03-cadastro.png) |
| Login | ![](telas/04-login.png) |
| Carrinho | ![](telas/05-carrinho.png) |
| Checkout | ![](telas/06-checkout.png) |
| Acompanhamento do pedido | ![](telas/07-pedido-acompanhamento.png) |
| Meus pedidos | ![](telas/08-meus-pedidos.png) |
| Admin – pedidos | ![](telas/09-admin-pedidos.png) |
| Admin – produtos | ![](telas/10-admin-produtos.png) |
| Admin – editar produto | ![](telas/11-admin-editar-produto.png) |
| Vitrine no celular | ![](telas/12-vitrine-celular.png) |
