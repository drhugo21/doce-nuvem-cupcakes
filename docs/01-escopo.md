# 1. Escopo do projeto (revisado)

## Contexto
A Doce Nuvem é uma loja de cupcakes gourmet. O cliente já teve um app que não funcionou
e prejudicou a imagem da loja. Por isso o objetivo é um sistema simples e confiável
para vender pela internet.

## Objetivo
Uma loja virtual web e responsiva (funciona no celular) com quatro pilares definidos na PIT I:
**vitrine virtual, pedido eletrônico, pagamento e entrega.**

## Atores
| Ator | Descrição |
|---|---|
| Visitante | Navega na vitrine e monta o carrinho sem estar logado. |
| Cliente | Visitante cadastrado. Finaliza pedidos, paga, acompanha e cancela. |
| Administrador | Funcionário da loja. Gerencia produtos e o andamento dos pedidos. |

## Histórias de usuário (resumo do backlog)
Prioridade: A = mais alta.

| ID | História | Prioridade | Pontos |
|---|---|---|---|
| US01 | Como visitante, quero ver os cupcakes com foto, nome e preço para escolher o que comprar. | A | 3 |
| US02 | Como visitante, quero buscar por sabor e filtrar por categoria para achar rápido o que procuro. | B | 2 |
| US03 | Como visitante, quero ver os detalhes de um cupcake (descrição e estoque). | B | 2 |
| US04 | Como visitante, quero me cadastrar para poder fazer pedidos. | A | 3 |
| US05 | Como cliente, quero entrar e sair da minha conta com segurança. | A | 2 |
| US06 | Como visitante, quero adicionar, alterar e remover itens do carrinho. | A | 5 |
| US07 | Como cliente, quero escolher entre entrega em casa e retirada na loja. | A | 3 |
| US08 | Como cliente, quero informar e reutilizar meu endereço de entrega. | B | 3 |
| US09 | Como cliente, quero pagar com PIX, cartão ou dinheiro na entrega. | A | 5 |
| US10 | Como cliente, quero ver o valor do frete e saber quanto falta para o frete grátis. | C | 2 |
| US11 | Como cliente, quero acompanhar o status do meu pedido. | A | 3 |
| US12 | Como cliente, quero cancelar um pedido que ainda não entrou em preparo. | B | 2 |
| US13 | Como cliente, quero ver o histórico dos meus pedidos. | C | 2 |
| US14 | Como administrador, quero cadastrar e editar produtos, preço e estoque. | A | 5 |
| US15 | Como administrador, quero ver os pedidos e avançar o status de cada um. | A | 3 |
| US16 | Como administrador, quero filtrar os pedidos por status. | C | 1 |

## Regras de negócio
| ID | Regra |
|---|---|
| RN01 | Pedido mínimo de R$ 15,00. |
| RN02 | Taxa de entrega de R$ 8,00, grátis em pedidos a partir de R$ 100,00. Retirada na loja é sempre grátis. |
| RN03 | Não é possível comprar mais do que o estoque. O estoque é baixado quando o pedido é confirmado. |
| RN04 | PIX e cartão são aprovados na hora (simulação). Dinheiro fica "Aguardando pagamento". |
| RN05 | O cliente só cancela pedidos "Aguardando pagamento" ou "Pago". Ao cancelar, o estoque volta. |
| RN06 | Fluxo do pedido: Aguardando pagamento → Pago → Em preparo → Saiu para entrega (ou Pronto para retirada) → Entregue. |
| RN07 | Um cliente só vê os próprios pedidos. Apenas o administrador acessa o painel. |

## Requisitos não funcionais
| ID | Requisito |
|---|---|
| RNF01 | Interface responsiva (celular e computador). |
| RNF02 | Senhas guardadas com hash. Dados de cartão nunca são armazenados. |
| RNF03 | Mensagens de erro claras em português em todos os formulários. |
| RNF04 | Acessibilidade básica: rótulos nos campos, link "pular para o conteúdo", foco visível. |
| RNF05 | Back-end em Python/Flask com padrão MVC e banco PostgreSQL. |

## Fora do escopo
Integração real com gateway de pagamento, cálculo de frete por CEP e notificações por e-mail.
