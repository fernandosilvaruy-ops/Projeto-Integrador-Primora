       ##Tabela de Clientes ##
CREATE TABLE IF NOT EXISTS clientes_tratados (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    cnpj_cpf VARCHAR(20) UNIQUE NOT NULL,
    cidade VARCHAR(100),
    estado VARCHAR(2),
    data_cadastro DATE,
    data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

     ## Tabelo de auditoria ## 
CREATE TABLE IF NOT EXISTS auditoria_etl (
    id SERIAL PRIMARY KEY,
    nome_pipeline VARCHAR(100) NOT NULL,
    status_execucao VARCHAR(50) NOT NULL, -- Ex: 'SUCESSO', 'ERRO'
    linhas_processadas INT DEFAULT 0,
    mensagem_erro TEXT,
    data_execucao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);