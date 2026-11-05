
# Trabalho-de-Conclus-o-de-Curso

Projeto Integrador (Bolsa Futuro Digital) · Desafio Técnico 1 · **ETL, limpeza e enriquecimento de dados** da base de clientes da *Distribuidora Vetor* (empresa fictícia).

O projeto recebe um CSV de clientes com dados sujos (bairros escritos de vários jeitos, CNPJ, telefone e data em formatos diferentes, CEPs ausentes ou inválidos) e produz uma base limpa, guardada em PostgreSQL, com registro de cada alteração feita.

> Documentação completa em [`docs/`](docs/): [Documentação técnica](docs/DOCUMENTACAO_TECNICA.md) · [Regras de negócio](docs/REGRAS_DE_NEGOCIO.md) · [Estrutura dos documentos](docs/ESTRUTURA_DOCUMENTOS.md)

---

## 1. Status do projeto

| Etapa | Situação |
|---|---|
| Diagnóstico dos dados (CNPJ, telefone, data, bairros) | Pronto |
| Funções de limpeza (CNPJ, telefone, data, bairro, CEP) | Pronto |
| Testes unitários das funções de limpeza | Pronto |
| Conexão Python ↔ PostgreSQL (SQLAlchemy + `.env`) | Pronto |
| Serviço de consulta de CEP com cache local | Pronto |
| App Django `cliente` (modelo, migrations, importação do CSV) | Pronto |
| Lógica de decisão: bairro digitado × bairro da API | Em desenvolvimento |
| Tabela e módulo de auditoria | Em desenvolvimento |
| Carga final no PostgreSQL (`loader.py`) | Em desenvolvimento |
| Testes da API de CEP com mocks | Em desenvolvimento |
| Pipeline unificado (`main.py`) | Em desenvolvimento |

Este README descreve o que **já existe**. Os itens "em desenvolvimento" estão marcados como tal nas seções abaixo e serão atualizados quando forem concluídos.

---

## 2. Requisitos

- **Python 3.12 ou superior** (exigência do Django 6.x; confira com `python --version`)
- **PostgreSQL** instalado localmente, na porta padrão `5432`
- **Git**
- Acesso à internet (somente para consultar CEPs na API ViaCEP)

As bibliotecas Python estão no arquivo `requirements.txt` (Django, SQLAlchemy, psycopg2, pandas, python-dotenv, requests, pytest, entre outras).

---

## 3. Instalação

### 3.1 Baixar o projeto

```bash
git clone https://github.com/fernandosilvaruy-ops/Projeto-Integrador-Primora.git
cd Projeto-Integrador-Primora
```

### 3.2 Criar e ativar o ambiente virtual

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\activate
```

Linux ou macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.3 Instalar as bibliotecas

```bash
pip install -r requirements.txt
```

### 3.4 Configurar as variáveis de ambiente (`.env`)

As senhas **não** ficam no código. Cada pessoa cria o seu próprio arquivo `.env` na **raiz do projeto**, a partir do modelo:

```bash
copy .env.example .env        # Windows
cp .env.example .env          # Linux ou macOS
```

Abra o `.env` e preencha:

| Variável | O que é | Exemplo |
|---|---|---|
| `DB_NAME` | Nome do banco | `distribuidora_vetor` |
| `DB_USER` | Usuário do PostgreSQL | `postgres` |
| `DB_PASSWORD` | Senha do PostgreSQL (definida na instalação) | *(a sua)* |
| `DB_HOST` | Endereço do banco | `localhost` |
| `DB_PORT` | Porta | `5432` |
| `DJANGO_SECRET_KEY` | Chave secreta do Django | *(gere uma, veja abaixo)* |

Para gerar a `DJANGO_SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

> O `.env` está no `.gitignore`: **nunca** suba esse arquivo para o GitHub.

---

## 4. Banco de dados

### 4.1 Criar o banco

No PostgreSQL (pelo pgAdmin ou pelo `psql`), crie o banco com o mesmo nome definido em `DB_NAME`:

```sql
CREATE DATABASE distribuidora_vetor;
```

### 4.2 Criar as tabelas do Django

```bash
cd web
python manage.py migrate
```

Isso cria a tabela `cliente_cliente` (modelo `Cliente`) e as tabelas internas do Django.

### 4.3 Importar o CSV para o banco

Ainda dentro da pasta `web`:

```bash
python manage.py importar_clientes
```

O comando lê o arquivo `clientes_distribuidora_vetor.csv` (na raiz do projeto) e grava cada cliente em `cliente_cliente`. Ele pode ser executado mais de uma vez sem duplicar clientes, porque atualiza o registro quando o CNPJ já existe. No final, mostra quantos clientes foram processados.

> Esse comando grava os dados **como vieram no CSV**, sem aplicar as funções de limpeza. A base tratada é uma etapa separada (veja a seção 5).

### 4.4 Testar a conexão (SQLAlchemy)

Na raiz do projeto, com o `.env` preenchido e as migrations aplicadas:

```bash
python src/database/connection.py
```

O script mostra a versão do PostgreSQL, quantos clientes existem em `cliente_cliente` e faz um teste de escrita e leitura numa tabela temporária.

### 4.5 Tabelas SQL de apoio

O arquivo `init.sql` define as tabelas `clientes_tratados` (base final) e `auditoria_etl` (registro das execuções). A carga final nelas faz parte das etapas em desenvolvimento (seção 1).

---

## 5. Executar a limpeza e as consultas

### 5.1 Limpar a base de clientes

Na pasta onde estão `padronizar_Clientes.py` e o CSV:

```bash
python padronizar_Clientes.py clientes_distribuidora_vetor.csv
```

Gera o arquivo `clientes_padronizado.csv` com as colunas originais mais as colunas tratadas (`cnpj_padronizado`, `telefone_padronizado`, `data_cadastro_padronizada`, `bairro_padronizado`, `cep_padronizado`, `cnpj_valido`) e imprime um resumo na tela.

### 5.2 Scripts de diagnóstico

```bash
python analise_clientes.py        # conta os formatos de CNPJ, telefone e data
python mapeamento_Bairros.py      # lista as grafias de bairro e gera mapeamento_bairros.csv
```

### 5.3 Consulta de CEP

O módulo `cep_servico.py` consulta o ViaCEP e guarda cada resposta em `cache_cep.json`. Na segunda consulta ao mesmo CEP, a resposta vem do cache, sem usar a internet. Para ver funcionando, na raiz do projeto:

```bash
python teste_cep.py
```

### 5.4 Pipeline completo

> **Em desenvolvimento.** O objetivo é rodar extração, transformação, enriquecimento, auditoria e carga com um único comando (`python main.py`). Esta seção será atualizada quando o `main.py` estiver pronto.

---

## 6. Testes

Os testes automatizados ficam na pasta `tests/` e usam o **pytest**. Com o ambiente virtual ativo, na raiz do projeto:

```bash
python -m pytest -v
```

Cobrem a limpeza de CNPJ, telefone e data, a padronização de bairros e o tratamento de valores nulos ou vazios. Não usam internet nem banco de dados. Os testes da consulta de CEP, com respostas simuladas (mocks), estão em desenvolvimento.

---

## 7. Estrutura do projeto

```
Projeto-Integrador-Primora/
├── .env.example                  modelo das variáveis de ambiente
├── .gitignore
├── requirements.txt              bibliotecas do projeto
├── init.sql                      tabelas clientes_tratados e auditoria_etl
├── clientes_distribuidora_vetor.csv   base original (47 clientes fictícios)
├── web/                          projeto Django
│   ├── manage.py
│   ├── core/                     configurações (settings, urls, wsgi, asgi)
│   └── cliente/                  app de clientes
│       ├── models.py             modelo Cliente
│       ├── migrations/           histórico das mudanças no banco
│       └── management/commands/importar_clientes.py
├── src/database/connection.py    conexão SQLAlchemy com o PostgreSQL
├── tests/                        testes automatizados (pytest)
└── docs/                         documentação do projeto
```

Também fazem parte do projeto os scripts de dados `padronizar_Clientes.py`, `analise_clientes.py` e `mapeamento_Bairros.py`, e o serviço de CEP (`cep_servico.py` e `cache_cep.json`).

> A estrutura acima foi montada a partir dos caminhos usados no código. Confira com `git ls-files` e ajuste se alguma pasta estiver em outro lugar.

---

## 8. Regras de negócio

As regras adotadas (como cada campo é limpo, o que é considerado válido e o que acontece com dados que não podem ser corrigidos) estão em [regras de negocio](REGRAS_DE_NEGOCIO.md). Os limites conhecidos da abordagem estão na [documentação técnica](docs/DOCUMENTACAO_TECNICA.md#10-limites-conhecidos).

---

## 9. Licença

Veja o arquivo [`LICENSE`](LICENSE).
