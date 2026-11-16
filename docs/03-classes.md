# 3. Diagrama de classes

```mermaid
classDiagram
    class Usuario {
      +int id
      +str nome
      +str email
      +str senha_hash
      +str telefone
      +bool is_admin
      +datetime criado_em
      +definir_senha(senha)
      +verificar_senha(senha) bool
    }
    class Categoria {
      +int id
      +str nome
    }
    class Produto {
      +int id
      +str nome
      +str descricao
      +Decimal preco
      +int estoque
      +str cor
      +bool ativo
      +disponivel() bool
    }
    class Endereco {
      +int id
      +str cep
      +str logradouro
      +str numero
      +str complemento
      +str bairro
      +str cidade
      +str uf
      +formatado() str
    }
    class Pedido {
      +int id
      +str status
      +str tipo_entrega
      +str endereco_entrega
      +str forma_pagamento
      +Decimal subtotal
      +Decimal frete
      +Decimal total
      +str observacao
      +datetime criado_em
      +pode_cancelar() bool
      +proximo_status() str
    }
    class ItemPedido {
      +int id
      +int quantidade
      +Decimal preco_unitario
      +subtotal() Decimal
    }
    class Carrinho {
      <<service>>
      +adicionar(produto_id, qtd)
      +atualizar(produto_id, qtd)
      +remover(produto_id)
      +itens() list
      +subtotal() Decimal
      +limpar()
    }
    class OrderService {
      <<service>>
      +calcular_frete(subtotal, tipo) Decimal
      +validar_cartao(numero, validade, cvv)
      +criar_pedido(...) Pedido
      +cancelar_pedido(pedido)
      +avancar_status(pedido) str
    }

    Usuario "1" --> "0..*" Endereco : possui
    Usuario "1" --> "0..*" Pedido : faz
    Categoria "1" --> "0..*" Produto : agrupa
    Pedido "1" *-- "1..*" ItemPedido : contém
    ItemPedido "0..*" --> "1" Produto : refere-se
    Carrinho ..> Produto : usa
    OrderService ..> Carrinho : lê
    OrderService ..> Pedido : cria
```

## Arquitetura MVC
| Camada | Onde fica | Responsabilidade |
|---|---|---|
| Model | `app/models.py` | Entidades e mapeamento para o PostgreSQL (SQLAlchemy). |
| View | `app/templates/` | Páginas HTML (Jinja2), CSS e JavaScript. |
| Controller | `app/controllers/` | Recebe as requisições, chama os serviços e escolhe a view. |
| Serviços | `app/services/` | Regras de negócio (carrinho, frete, pagamento, validações). |
