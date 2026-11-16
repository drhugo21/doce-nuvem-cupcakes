"""Carrinho de compras guardado na sessão do usuário."""
from decimal import Decimal

from flask import session

from .. import db
from ..models import Produto

MAX_POR_ITEM = 50


class ErroCarrinho(Exception):
    pass


class Carrinho:
    CHAVE = "carrinho"

    def _dados(self):
        return session.setdefault(self.CHAVE, {})

    def _salvar(self, dados):
        session[self.CHAVE] = dados
        session.modified = True

    def adicionar(self, produto_id, quantidade=1):
        if quantidade < 1:
            raise ErroCarrinho("Quantidade inválida.")
        produto = db.session.get(Produto, produto_id)
        if not produto or not produto.ativo:
            raise ErroCarrinho("Produto não encontrado.")
        dados = self._dados()
        nova = dados.get(str(produto_id), 0) + quantidade
        if nova > produto.estoque:
            raise ErroCarrinho(f"Só temos {produto.estoque} unidade(s) de {produto.nome} em estoque.")
        if nova > MAX_POR_ITEM:
            raise ErroCarrinho(f"Máximo de {MAX_POR_ITEM} unidades por produto.")
        dados[str(produto_id)] = nova
        self._salvar(dados)
        return produto

    def atualizar(self, produto_id, quantidade):
        dados = self._dados()
        if quantidade <= 0:
            dados.pop(str(produto_id), None)
            self._salvar(dados)
            return
        produto = db.session.get(Produto, produto_id)
        if not produto:
            raise ErroCarrinho("Produto não encontrado.")
        if quantidade > produto.estoque:
            raise ErroCarrinho(f"Só temos {produto.estoque} unidade(s) de {produto.nome} em estoque.")
        dados[str(produto_id)] = min(quantidade, MAX_POR_ITEM)
        self._salvar(dados)

    def remover(self, produto_id):
        self.atualizar(produto_id, 0)

    def limpar(self):
        self._salvar({})

    def itens(self):
        """Lista de (produto, quantidade, subtotal); descarta produtos que sumiram."""
        resultado = []
        for pid, qtd in list(self._dados().items()):
            produto = db.session.get(Produto, int(pid))
            if produto and produto.ativo:
                resultado.append((produto, qtd, produto.preco * qtd))
        return resultado

    def subtotal(self):
        return sum((s for _, _, s in self.itens()), Decimal("0.00"))

    def quantidade_total(self):
        return sum(session.get(self.CHAVE, {}).values())

    def vazio(self):
        return not self._dados()
