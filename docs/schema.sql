-- Projeto físico (PostgreSQL), gerado a partir dos models SQLAlchemy

CREATE TABLE categorias (
	id SERIAL NOT NULL, 
	nome VARCHAR(60) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
);

CREATE TABLE usuarios (
	id SERIAL NOT NULL, 
	nome VARCHAR(120) NOT NULL, 
	email VARCHAR(160) NOT NULL, 
	senha_hash VARCHAR(256) NOT NULL, 
	telefone VARCHAR(20), 
	is_admin BOOLEAN NOT NULL, 
	criado_em TIMESTAMP WITH TIME ZONE, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_usuarios_email ON usuarios (email);

CREATE TABLE enderecos (
	id SERIAL NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	cep VARCHAR(9) NOT NULL, 
	logradouro VARCHAR(160) NOT NULL, 
	numero VARCHAR(10) NOT NULL, 
	complemento VARCHAR(60), 
	bairro VARCHAR(80) NOT NULL, 
	cidade VARCHAR(80) NOT NULL, 
	uf VARCHAR(2) NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);

CREATE TABLE pedidos (
	id SERIAL NOT NULL, 
	usuario_id INTEGER NOT NULL, 
	status VARCHAR(30) NOT NULL, 
	tipo_entrega VARCHAR(10) NOT NULL, 
	endereco_entrega VARCHAR(300), 
	forma_pagamento VARCHAR(20) NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	frete NUMERIC(10, 2) NOT NULL, 
	total NUMERIC(10, 2) NOT NULL, 
	observacao VARCHAR(300), 
	criado_em TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(usuario_id) REFERENCES usuarios (id)
);

CREATE TABLE produtos (
	id SERIAL NOT NULL, 
	nome VARCHAR(120) NOT NULL, 
	descricao TEXT NOT NULL, 
	preco NUMERIC(10, 2) NOT NULL, 
	estoque INTEGER NOT NULL, 
	cor VARCHAR(7) NOT NULL, 
	ativo BOOLEAN NOT NULL, 
	categoria_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_produto_preco_positivo CHECK (preco > 0), 
	CONSTRAINT ck_produto_estoque_nao_negativo CHECK (estoque >= 0), 
	FOREIGN KEY(categoria_id) REFERENCES categorias (id)
);

CREATE TABLE itens_pedido (
	id SERIAL NOT NULL, 
	pedido_id INTEGER NOT NULL, 
	produto_id INTEGER NOT NULL, 
	quantidade INTEGER NOT NULL, 
	preco_unitario NUMERIC(10, 2) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_item_qtd_positiva CHECK (quantidade > 0), 
	FOREIGN KEY(pedido_id) REFERENCES pedidos (id), 
	FOREIGN KEY(produto_id) REFERENCES produtos (id)
);

