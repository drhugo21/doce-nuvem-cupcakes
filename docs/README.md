# Documentação – Doce Nuvem Cupcakes

Revisão da documentação da PIT I (melhoria contínua), atualizada para o sistema implementado na PIT II.

1. [Escopo, histórias de usuário e regras de negócio](01-escopo.md)
2. [Casos de uso (diagrama e expandidos)](02-casos-de-uso.md)
3. [Diagrama de classes e arquitetura MVC](03-classes.md)
4. [Banco de dados: modelo, normalização e dicionário de dados](04-banco-de-dados.md) · [script físico](schema.sql)
5. [Telas, mapa navegacional e mensagens de erro](05-telas.md)

## O que mudou em relação à PIT I
- **Escopo:** foram incluídos o perfil de administrador e as regras de negócio explícitas (RN01 a RN07).
- **Pagamento:** ficou definido como simulado (PIX, cartão e dinheiro), sem armazenar dados de cartão.
- **Entrega:** ganhou a opção de retirada na loja e a regra de frete grátis.
- **Banco de dados:** foram feitos os projetos conceitual, lógico e físico (que não existiam na PIT I), com dicionário de dados.
- **Telas:** os protótipos foram substituídos pelas telas reais, com acessibilidade e versão para celular.
