CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150),
    telefone VARCHAR(30) NOT NULL UNIQUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS atendimentos (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    mensagem TEXT NOT NULL,
    intencao VARCHAR(100),
    resposta TEXT,
    status VARCHAR(50) DEFAULT 'aberto',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS protocolos (
    id SERIAL PRIMARY KEY,
    atendimento_id INTEGER REFERENCES atendimentos(id),
    numero VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'aberto',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
