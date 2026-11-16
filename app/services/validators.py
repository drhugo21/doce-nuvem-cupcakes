import re

UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
       "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}


def email_valido(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or ""))


def validar_cadastro(nome, email, senha, confirmacao):
    erros = []
    if len((nome or "").strip()) < 3:
        erros.append("Informe seu nome completo.")
    if not email_valido(email):
        erros.append("E-mail inválido.")
    if len(senha or "") < 6:
        erros.append("A senha deve ter pelo menos 6 caracteres.")
    if senha != confirmacao:
        erros.append("As senhas não conferem.")
    return erros


def validar_endereco(f):
    erros = []
    if not re.fullmatch(r"\d{5}-?\d{3}", f.get("cep", "").strip()):
        erros.append("CEP inválido (use 00000-000).")
    for campo, rotulo in [("logradouro", "Rua"), ("numero", "Número"),
                          ("bairro", "Bairro"), ("cidade", "Cidade")]:
        if not f.get(campo, "").strip():
            erros.append(f"{rotulo} é obrigatório.")
    if f.get("uf", "").strip().upper() not in UFS:
        erros.append("UF inválida.")
    return erros


def validar_produto(f):
    erros = []
    if len(f.get("nome", "").strip()) < 3:
        erros.append("Nome do produto muito curto.")
    try:
        if float(f.get("preco", "").replace(",", ".")) <= 0:
            erros.append("Preço deve ser maior que zero.")
    except ValueError:
        erros.append("Preço inválido.")
    try:
        if int(f.get("estoque", "")) < 0:
            erros.append("Estoque não pode ser negativo.")
    except ValueError:
        erros.append("Estoque inválido.")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", f.get("cor", "#f8bbd0")):
        erros.append("Cor inválida.")
    return erros
