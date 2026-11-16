# Laudo de qualidade: Doce Nuvem Cupcakes

**Período de testes:** 10/11/2026 a 12/11/2026. **Correções:** 15/11/2026.
**Testes de aceitação:** 5 testadores, usando o [formulário de teste](formulario-teste.md).
**Testes automatizados:** pytest. Antes das correções eram 39 testes; foram incluídos 5 de regressão, e hoje os 44 passam.

## Defeitos encontrados e correções
| # | Defeito (quem apontou) | Severidade | Correção | Evidência antes → depois | Situação |
|---|---|---|---|---|---|
| D1 | Horário do pedido aparecia 3 h adiantado: gravado em UTC e exibido sem conversão (Ana Paula) | Média | Filtro `data_local` converte para America/Sao_Paulo; a data passou a aparecer também na página do pedido | [B03](evidencias/B03-antes-horario-utc.png) → [A03](evidencias/A03-depois-horario-brasilia.png) | Corrigido |
| D2 | No celular, a tabela do carrinho escondia o subtotal e o botão Remover, com rolagem lateral (Bruno) | Alta | Carrinho em formato de cartões em telas pequenas | [B02](evidencias/B02-antes-carrinho-celular.png) → [A02](evidencias/A02-depois-carrinho-celular.png) | Corrigido |
| D3 | Coluna "Ações" do painel admin desalinhada e quebrando a borda da tabela (Camila) | Baixa | Botões agrupados num `div` flexível dentro da célula | [B01](evidencias/B01-antes-admin-acoes.png) → [A01](evidencias/A01-depois-admin-acoes.png) | Corrigido |
| D4 | O campo "voltar" do carrinho aceitava endereço externo (redirecionamento aberto, risco de phishing) (Diego) | Alta | Só aceita caminhos internos; o mesmo vale para o `next` do login | [antes](evidencias/antes-terminal.txt) → [depois](evidencias/depois-terminal.txt) | Corrigido |
| D5 | Formulários sem proteção CSRF, e o "Sair" funcionava por link GET (Diego) | Alta | Token CSRF em todos os formulários POST; logout só por POST | [antes](evidencias/antes-terminal.txt) → [depois](evidencias/depois-terminal.txt) | Corrigido |
| D6 | Telefone aceitava letras no cadastro (Elisa) | Baixa | Validação no formato (11) 91234-5678 | [antes](evidencias/antes-terminal.txt) → [A06](evidencias/A06-depois-telefone-invalido.png) | Corrigido |

## Sugestões e funcionalidades não testadas
| Item | Decisão |
|---|---|
| Preencher o endereço automaticamente pelo CEP (Elisa) | Melhoria aceita para uma próxima versão (integração ViaCEP). |
| Recuperação de senha (Ana Paula) | Não implementada; fica para uma próxima versão. |
| Cadastro de categorias pelo painel (Camila) | Não implementado; as categorias são criadas pelo `flask seed`. |
| Pagamento real com gateway (Bruno, Elisa) | Fora do escopo: o pagamento é simulado (ver escopo). |

## Conclusão
Todos os fluxos principais funcionaram nos 5 testes: vitrine, carrinho, pedido, pagamento, entrega, acompanhamento e painel.
Os 6 defeitos apontados foram corrigidos e cada um ganhou um teste automatizado de regressão
(`tests/test_correcoes.py`). As melhorias restantes foram registradas para versões futuras.
